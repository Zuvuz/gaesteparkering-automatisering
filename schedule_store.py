import json
from pathlib import Path
from datetime import datetime, timedelta

PENDING_EXPIRY = timedelta(hours=24)
SCHEDULE_FILE = Path(__file__).resolve().parent / "schedule.json"


def load_jobs():
    if SCHEDULE_FILE.exists():
        with open(SCHEDULE_FILE) as f:
            return json.load(f)
    return []


def save_jobs(jobs):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(jobs, f, indent=2)


def add_group(name, plate, email, times):
    jobs = load_jobs()
    group_id = f"{name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    total = len(times)

    for index, t in enumerate(times, start=1):
        jobs.append({
            "group_id": group_id,
            "name": name,
            "plate": plate,
            "email": email,
            "scheduled_time": t.isoformat(),
            "status": "pending",
            "index": index,
            "total": total,
        })

    save_jobs(jobs)
    return group_id, total


if __name__ == "__main__":
    from scheduler import compute_schedule

    times = compute_schedule(datetime(2026, 9, 8, 10, 0), datetime(2026, 9, 8, 20, 0))
    group_id, total = add_group("mor", "DZ18927", "runen8800@gmail.com", times)
    print("Oprettet gruppe:", group_id, "med", total, "registreringer")


PENDING_FILE = Path(__file__).resolve().parent / "pending_confirmation.json"


def get_pending_confirmation():
    if not PENDING_FILE.exists():
        return None

    with open(PENDING_FILE) as f:
        data = json.load(f)

    if not data:
        return None

    created_at = datetime.fromisoformat(data["created_at"])
    if datetime.now() - created_at > PENDING_EXPIRY:
        clear_pending_confirmation()
        return None

    return data


def set_pending_confirmation(data):
    data = dict(data)
    data["created_at"] = datetime.now().isoformat()
    with open(PENDING_FILE, "w") as f:
        json.dump(data, f, indent=2)

def clear_pending_confirmation():
    with open(PENDING_FILE, "w") as f:
        json.dump(None, f)


def extend_group(group_id):
    from scheduler import RENEWAL_INTERVAL
    from datetime import datetime

    jobs = load_jobs()
    group_jobs = [j for j in jobs if j["group_id"] == group_id]
    if not group_jobs:
        return None

    last_job = max(group_jobs, key=lambda j: j["index"])
    next_time = datetime.fromisoformat(last_job["scheduled_time"]) + RENEWAL_INTERVAL
    new_total = last_job["total"] + 1

    new_job = {
        "group_id": group_id,
        "name": last_job["name"],
        "plate": last_job["plate"],
        "email": last_job["email"],
        "scheduled_time": next_time.isoformat(),
        "status": "pending",
        "index": new_total,
        "total": new_total,
    }
    jobs.append(new_job)
    save_jobs(jobs)
    return new_job
