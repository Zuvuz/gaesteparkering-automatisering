import json
from pathlib import Path

PEOPLE_FILE = Path(__file__).resolve().parent / "people.json"


def load_people():
    if PEOPLE_FILE.exists():
        with open(PEOPLE_FILE) as f:
            return json.load(f)
    return {}


def save_people(people):
    with open(PEOPLE_FILE, "w") as f:
        json.dump(people, f, indent=2, ensure_ascii=False)


def add_person(name, plate, email):
    people = load_people()
    name = name.lower()
    is_new = name not in people
    people[name] = {"plate": plate.upper(), "email": email}
    save_people(people)
    return is_new


if __name__ == "__main__":
    is_new = add_person("test_person", "AB12345", "test@example.com")
    print("Ny person?", is_new)
    print(load_people())
