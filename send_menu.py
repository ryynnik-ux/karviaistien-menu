import os
import re
import json
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

THIS_WEEK_URL = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/"
NEXT_WEEK_URL = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/2/"


def get_page_data(url):

    response = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    response.raise_for_status()

    html = response.text

    match = re.search(
        r'var d=(\{.*?\});if\(typeof window',
        html,
        re.DOTALL
    )

    if not match:
        raise Exception("pageData JSON ei löytynyt")

    data = json.loads(match.group(1))

    return data


def clean_name(text):

    text = re.sub(r"\s*\([^)]*\)", "", text)
    text = text.replace("â¥", "")
    return text.strip()


def parse_week(url):

    data = get_page_data(url)

    days = data["result"]["pageContext"]["menu"]["Days"]

    output = []

    for day in days:

        output.append(f"📌 {day['Date']}")
        output.append("")

        for idx, meal in enumerate(day["Meals"]):

            icon = "🥦" if idx == 0 else "🍗"

            nutritions = meal.get("Nutritions", [])

            if not nutritions:
                continue

            main_course = clean_name(nutritions[0]["Name"])

            output.append(f"{icon} {main_course}")

            for side in nutritions[1:]:
                output.append(
                    f"   • {clean_name(side['Name'])}"
                )

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

    this_week = parse_week(THIS_WEEK_URL)
    next_week = parse_week(NEXT_WEEK_URL)

    message = (
        "🍽 Karviaistien koulu\n\n"
        "📅 TÄMÄ VIIKKO\n\n
