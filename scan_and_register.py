import json
import subprocess
import re
from datetime import datetime, timedelta
from register_car import register_car

with open("cars.json") as f:
    cars = json.load(f)

print(cars)
print(type(cars))

result = subprocess.run(
    ["sudo", "arp-scan", "--localnet", "--quiet", "--retry=2"],
    capture_output=True,
    text=True,
)
print(result.stdout)

mac_pattern = r"[0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}"
found_macs = re.findall(mac_pattern, result.stdout)

print(found_macs)

try: 
    with open("state.json") as f:
         state = json.load(f)
except FileNotFoundError:
    state = {}

now = datetime.now()


for mac in found_macs:
    if mac not in cars:
        print(f"Ukendt enhed: {mac}")
        continue

    car = cars[mac]
    last_str = state.get(mac)

    if last_str:
       last_time = datetime.fromisoformat(last_str)
       if now - last_time < timedelta(hours=7, minutes=45):
           print(f"{car['name']} er registreret for nyligt ({last_str}) - springer over.")
           continue

    print(f"Registrerer {car['name']} ({car['plate']})...")
    success = register_car(car["plate"], car["email"])

    if success:
        state[mac] = now.isoformat()
        print(f"{car['name']} registreret!")
    else:
        print(f"Kunne ikke registrere {car['name']}")


with open("state.json", "w") as f:
    json.dump(state, f, indent=2)
