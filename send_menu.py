import os
import re
import json
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

THIS_WEEK_URL = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/"
NEXT_WEEK_URL = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/2/"


def fetch_menu(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    html = response.text

    start_marker = 'window.pageData=d='
    end_marker = ';if(typeof window!=="undefined"'

    start = html.find(start_marker)

    if start == -1:
        raise Exception("pageData JSON ei löytynyt")

    start += len(start_marker)

    end = html.find(end_marker, start)

    if end == -1:
        raise Exception("pageData JSON loppua ei löytynyt")

    json_text = html[start:end]

    data = json.loads(json_text)

    days = data["result"]["pageContext"]["menu"]["Days"]

    output = []

    for day in days:

        output.append(f"📌 {day['Date']}")

        meals = day.get("Meals", [])

        for idx, meal in enumerate(meals):

            nutritions = meal.get("Nutritions", [])

            if not nutritions:
                continue

            icon = "🥦" if idx == 0 else "🍗"

            main_course = nutritions[0]["Name"]

            output.append("")
            output.append(f"{icon} {main_course}")

            for side in nutritions[1:]:
                output.append(f"   • {side['Name']}")

        output.append("")

    return "\n".join(output)


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

        this_week = fetch_menu(THIS_WEEK_URL)
        next_week = fetch_menu(NEXT_WEEK_URL)

        message = (
            "🍽 Karviaistien koulu\n\n"
            "📅 TÄMÄ VIIKKO\n\n"
            f"{this_week}\n\n"
            "─────────────────\n\n"
            "📅 ENSI VIIKKO\n\n"
            f"{next_week}"
        )

        send_message(message)

    except Exception as e:

        error_message = (
            "❌ Ruokalistan haku epäonnistui\n\n"
            f"{str(e)}"
        )

        try:
            send_message(error_message)
        except:
            pass

        raise
