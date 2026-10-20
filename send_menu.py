import os
import re
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

MENU_URL = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/2/"


def fetch_menu():
    response = requests.get(MENU_URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text("\n", strip=True)

print("===== DEBUG ALKU =====")
print(text[:5000])
print("===== DEBUG LOPPU =====")

    days = [
        "maanantai",
        "tiistai",
        "keskiviikko",
        "torstai",
        "perjantai"
    ]

    result = []

    lower = text.lower()

    for i, day in enumerate(days):
        start = lower.find(day)

        if start == -1:
            continue

        end = len(text)

        for next_day in days[i+1:]:
            pos = lower.find(next_day, start + 1)
            if pos != -1:
                end = pos
                break

        section = text[start:end]

        lines = [
            line.strip()
            for line in section.splitlines()
            if line.strip()
        ]

        menu_name = ""

        for line in lines:
            if (
                len(line) > 10
                and "ainesosat" not in line.lower()
                and "ravintosisältö" not in line.lower()
            ):
                menu_name = line
                break

        result.append(
            f"• {day.capitalize()}\n{menu_name}"
        )

    return "\n\n".join(result)


def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    ).raise_for_status()


if __name__ == "__main__":
    menu = fetch_menu()

    message = (
        "🍽 Karviaistien koulu\n"
        "📅 Ensi viikon ruokalista\n\n"
        f"{menu}"
    )

    send_message(message)
