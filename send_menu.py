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

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    paivat = [
        "maanantai",
        "tiistai",
        "keskiviikko",
        "torstai",
        "perjantai",
    ]

    tulos = []

    for i, line in enumerate(lines):

        lower = line.lower()

        if not any(lower.startswith(paiva) for paiva in paivat):
            continue

        paiva = line
        ruoat = []

        for j in range(i + 1, min(i + 50, len(lines))):

            rivi = lines[j]

            if any(rivi.lower().startswith(p) for p in paivat):
                break

            if (
                rivi.startswith("(")
                or "ainesosat" in rivi.lower()
                or "ravintosis" in rivi.lower()
                or "energia" in rivi.lower()
                or "proteiini" in rivi.lower()
                or "hiilihydraatit" in rivi.lower()
                or "rasva" in rivi.lower()
                or "suola" in rivi.lower()
                or rivi in ["0", "Lounas", "Lounas."]
            ):
                continue

            if len(rivi) < 4:
                continue

            if ":" in rivi:
                continue

            if rivi not in ruoat:
                ruoat.append(rivi)

        # Siivotaan yleisiä roskia
        siivotut = []

        for ruoka in ruoat:

            if any(
                sana in ruoka.lower()
                for sana in [
                    "ainesosat",
                    "ravintosis",
                    "energia",
                    "josta",
                    "kj",
                    "kcal",
                    "%",
                ]
            ):
                continue

            siivotut.append(ruoka)

        # Otetaan vain ensimmäiset varsinaiset ruoat
        siivotut = siivotut[:3]

        if siivotut:
            tulos.append(
                f"📌 {paiva}\n"
                + "\n".join(f"• {r}" for r in siivotut)
            )

    return "\n\n".join(tulos)


def send_message(message):
    response = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=30,
    )

    response.raise_for_status()


if __name__ == "__main__":

    try:
        menu = fetch_menu()

        message = (
            "🍽 Karviaistien koulu\n"
            "📅 Ensi viikon ruokalista\n\n"
            f"{menu}"
        )

        send_message(message)

    except Exception as e:

        send_message(
            f"❌ Ruokalistan haku epäonnistui:\n\n{str(e)}"
        )

        raise
