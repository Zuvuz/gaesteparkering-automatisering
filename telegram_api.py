import requests
import json
from pathlib import Path
from telegram_config import BOT_TOKEN, MY_USER_ID

STATE_FILE = Path(__file__).resolve().parent / "telegram_state.json"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(text, chat_id=MY_USER_ID):
    response = requests.post(f"{API_URL}/sendMessage", data={
        "chat_id": chat_id,
        "text": text,
    })
    return response.json()

def get_updates(offset=None, timeout=10):
    params = {"timeout": timeout}
    if offset is not None:
        params["offset"] = offset
    response = requests.get(f"{API_URL}/getUpdates", params=params, timeout=timeout + 5)
    return response.json()

def load_offset():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f).get("last_update_id")
    return None


def save_offset(update_id):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_update_id": update_id}, f)


def get_new_messages():
    last_id = load_offset()
    offset = last_id + 1 if last_id is not None else None
    data = get_updates(offset=offset, timeout=5)

    messages = []
    max_update_id = last_id

    for update in data.get("result", []):
        update_id = update["update_id"]
        if max_update_id is None or update_id > max_update_id:
            max_update_id = update_id

        message = update.get("message")
        if not message:
            continue
        if message["from"]["id"] != MY_USER_ID:
            continue  # ignorer alle andre end dig selv

        messages.append({"text": message.get("text", ""), "chat_id": message["chat"]["id"]})

    if max_update_id is not None:
        save_offset(max_update_id)

    return messages

if __name__ == "__main__":
    print(get_new_messages())
