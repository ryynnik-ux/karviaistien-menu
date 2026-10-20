import os
import re
import json
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

THIS_WEEK_URL = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/"
NEXT_WEEK_URL = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/2/"


def fix_text(text):
    try:
        return text.encode("latin1").decode("utf-8")
    except:
        return text


def get_page_data(url):

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    response.raise_for_status()

    html = response.text

    match = re.search(
        r'var d=(\{.*?"staticQueryHashes":\[\].*?"slicesMap":\{\}\})',
        html,
        re.DOTALL
    )

    if not match:
        raise Exception("Ruokalista-JSON ei löytynyt")

    data = json.loads(match.group(1))

    return data


def parse_week(url):

    data = get_page_data(url)

    days = data["result"]["pageContext"]["menu"]["Days"]

    output = []

    for day in days:

        output.append(f"📌 {fix_text(day['Date'])}")
        output.append("")

        for idx, meal in enumerate(day["Meals"]):

            icon = "🥦" if idx == 0 else "🍗"

            nutritions = meal.get("Nutritions", [])

            if not nutritions:
                continue

            main_course = fix_text(nutritions[0]["Name"])

            output.append(f"{icon} {main_course}")

            for side in nutritions[1:]:
                side_name = fix_text(side["Name"])
                output.append(f"   • {side_name}")

            output.append("")

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

        this_week = parse_week(THIS_WEEK_URL)

        next_week = parse_week(NEXT_WEEK_URL)

        message = (
            "🍽 Karviaistien koulu\n\n"
            "📅 TÄMÄ VIIKKO\n\n"
            f"{this_week}\n"
            "━━━━━━━━━━━━━━\n\n"
            "📅 ENSI VIIKKO\n\n"
            f"{next_week}"
        )

        send_message(message)

    except Exception as e:

        send_message(
            f"❌ Virhe ruokalistan haussa:\n\n{str(e)}"
        )

        raise
