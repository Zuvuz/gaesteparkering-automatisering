import json
import re
from people_store import load_people, add_person
from message_parser import parse_message
from scheduler import compute_schedule
from datetime import datetime
from register_car import register_car
from telegram_api import send_message, get_new_messages
from schedule_store import (
    load_jobs, save_jobs, add_group,
    get_pending_confirmation, set_pending_confirmation,
    clear_pending_confirmation, extend_group,
)


def process_due_jobs():
    jobs = load_jobs()
    now = datetime.now()
    changed = False

    for job in jobs:
        if job["status"] != "pending":
            continue

        scheduled_time = datetime.fromisoformat(job["scheduled_time"])
        if scheduled_time > now:
            continue

        print(f"Registrerer {job['name']} ({job['plate']}), {job['index']}/{job['total']}...")

        try:
            register_car(job["plate"], job["email"])
            success = True
            error_text = None
        except Exception as e:
            success = False
            error_text = str(e)

        changed = True

        if success:
            job["status"] = "done"
            send_message(
                f"✅ Registrering {job['index']}/{job['total']} for {job['name']} ({job['plate']}) lykkedes."
            )

            if job["index"] == job["total"] and job["total"] >= 4:
                set_pending_confirmation({"group_id": job["group_id"], "name": job["name"]})
                send_message(
                    f"Det var sidste planlagte registrering for {job['name']} "
                    f"({job['total']} i alt). Skal jeg forlænge med endnu en? Svar 'ja' eller 'nej'."
                )
        else:
            job["status"] = "failed"
            send_message(
                f"❌ Registrering {job['index']}/{job['total']} for {job['name']} ({job['plate']}) FEJLEDE: {error_text}"
            )

    if changed:
        save_jobs(jobs)



def handle_messages():
    people = load_people()
    messages = get_new_messages()

    for msg in messages:
        text = msg["text"].strip()
        lowered = text.lower()
        if lowered in ("help", "hjælp", "hjaelp"):
            send_message(
            "📋 Sådan bruger du parkeringsbotten:\n\n"
            "Registrer besøg:\n"
            "• \"Navn kommer kl 13\" - registrerer én gang i dag kl. 13\n"
            "• \"Navn kommer i morgen kl 10 til kl 20\" - registrerer automatisk det antal gange der skal til\n"
            "• \"Navn kommer den 15/9 kl 14 til 18/9 kl 10\" - samme, men med selvvalgte datoer\n\n"
            "Tilføj en person:\n"
            "• \"/tilfoej Navn Nummerplade Email\" - fx: /tilfoej Mor DZ18927 mor@email.dk\n\n"
            "Forlængelse:\n"
            "Ved 4+ registreringer spørger jeg automatisk om forlængelse, når den sidste er udført. Svar \"ja\" eller \"nej\".\n\n"
            "Skriv \"hjælp\" når som helst for at se denne besked igen."
            )
            continue
        add_match = re.match(r"^/tilf[øo]j\s+(\S+)\s+(\S+)\s+(\S+)\s*$", text, re.IGNORECASE)

        if text.lower().startswith("/tilf") and not add_match:
            send_message("Brug formatet: /tilfoej <navn> <nummerplade> <email>")
            continue

        if add_match:
            name, plate, email = add_match.groups()

            if "@" not in email:
                send_message(f"Ugyldig email: {email}")
                continue
            if not plate.isalnum():
                send_message(f"Ugyldig nummerplade (kun bogstaver/tal): {plate}")
                continue

            is_new = add_person(name, plate, email)
            people = load_people()
            action = "Tilføjet ny person" if is_new else "Opdateret eksisterende person"
            send_message(f"{action}: {name.lower()} ({plate.upper()}, {email})")
            continue

        if lowered in ("ja", "nej"):
            pending = get_pending_confirmation()
            if pending is None:
                send_message("Der er ikke noget at bekræfte lige nu.")
                continue

            if lowered == "ja":
                new_job = extend_group(pending["group_id"])
                clear_pending_confirmation()
                when = datetime.fromisoformat(new_job["scheduled_time"]).strftime("%d/%m kl. %H:%M")
                send_message(f"OK! Forlænger for {pending['name']} - ny registrering planlagt {when}.")
            else:
                clear_pending_confirmation()
                send_message(f"OK, forlænger ikke for {pending['name']}.")
            continue

        parsed = parse_message(text)

        if parsed is None:
            send_message(f'Forstod ikke beskeden: "{text}"')
            continue

        name = parsed["name"]
        if name not in people:
            send_message(f"Kender ikke navnet '{name}' - tjek people.json")
            continue

        pending = get_pending_confirmation()
        if pending is not None and pending["name"] == name:
            clear_pending_confirmation()

        person = people[name]
        times = compute_schedule(parsed["start"], parsed["end"])
        group_id, total = add_group(name, person["plate"], person["email"], times)

        first = times[0].strftime("%d/%m kl. %H:%M")
        last = times[-1].strftime("%d/%m kl. %H:%M")

        if total == 1:
            send_message(f"OK! Planlægger 1 registrering for {name} ({first}).")
        else:
            send_message(
                f"OK! Planlægger {total} registreringer for {name}, fra {first} til sidste forsøg {last}."
            )


if __name__ == "__main__":
    handle_messages()
    process_due_jobs()
