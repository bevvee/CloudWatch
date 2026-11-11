
import os
import requests

NTFY_SERVER = os.getenv(
    "NTFY_SERVER",
    "https://ntfy.sh"
)

NTFY_TOPIC = os.getenv(
    "NTFY_TOPIC",
    "coldwatch-alert-7f82a91c"
)

NTFY_TOKEN = os.getenv("NTFY_TOKEN", "")


def send_temperature_alert(temp, hum):
    url = f"{NTFY_SERVER.rstrip('/')}/{NTFY_TOPIC}"

    payload = {
        "temp": temp,
        "hum": hum,
        "message": "Critical temperature!"
    }

    headers = {
        "Content-Type": "application/json"
    }

    if NTFY_TOKEN:
        headers["Authorization"] = f"Bearer {NTFY_TOKEN}"

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

        print("ColdWatch alert sent successfully")
        return True

    except requests.RequestException as error:
        print("ntfy error:", error)
        return False
