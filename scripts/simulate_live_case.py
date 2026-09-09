"""Send a small, free local event stream to a running CarePulse instance."""
import json
import os
from urllib.request import Request, urlopen

BASE_URL = os.getenv("CARE_PULSE_BASE_URL", "http://127.0.0.1:8000")
events = [
    {"event_type": "CUSTOMER_MESSAGE", "actor_type": "customer", "message": "I am still waiting and have no update.", "metadata": {"channel": "chat"}},
    {"event_type": "CASE_TRANSFERRED", "actor_type": "system", "message": "Transferred for specialist review.", "metadata": {"channel": "chat"}},
    {"event_type": "AGENT_MESSAGE", "actor_type": "agent", "message": "I have taken ownership and will update you shortly.", "metadata": {"channel": "chat"}},
]
for event in events:
    body = {"case_id": "CP-00006", **event}
    req = Request(f"{BASE_URL}/api/events", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req) as response:
        result = json.loads(response.read().decode())
    print(f"{result['event_type']}: risk {result['risk']['score']}/100 ({result['risk']['band']})")
print("Live case simulation complete. Open /story or /simulator to inspect the updated intelligence.")
