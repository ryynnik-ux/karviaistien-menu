import os
import json
import re
import requests

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

THIS_WEEK_URL = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/"
NEXT_WEEK_URL = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/2/"


def extract_page_data(html):

    marker = 'window.pageData=d='

    start = html.find(marker)

    if start == -1:
        raise Exception("window.pageData ei löytynyt")

    start += len(marker)

    end = html.find("window.pageData=d;", start)

    print("START:", start)
    print("END:", end)

    print("HTML AROUND START")
    print(html[start:start + 500])

    raise Exception("DEBUG")
    
def format_meal(meal_name):

    meal_name = re.sub(r"\s*\([^)]*\)", "", meal_name)

    parts = [
        p.strip()
        for p in meal_name.split(",")
        if p.strip()
    ]

    if not parts:
        return ""

    result = []

    result.append(parts[0])

    for side in parts[1:]:
        result.append(f"   • {side}")

    return "\n".join(result)


def fetch_menu(url):

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    html = response.text

    page_data = extract_page_data(html)

    menu = page_data["pageContext"]["menu"]

    output = []

    for day in menu["Days"]:

        output.append(f"📌 {day['Date']}")
        output.append("")

        meals = day["Meals"]

        for idx, meal in enumerate(meals):

            icon = "🥦" if idx == 0 else "🍗"

            formatted = format_meal(meal["Name"])

            output.append(f"{icon} {formatted}")
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
            "━━━━━━━━━━━━━━\n\n"
            "📅 ENSI VIIKKO\n\n"
            f"{next_week}"
        )

        send_message(message)

    except Exception as e:

        try:
            send_message(
                f"❌ Ruokalistan haku epäonnistui:\n\n{str(e)}"
            )
        except:
            pass

        raise
