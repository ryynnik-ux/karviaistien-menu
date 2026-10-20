import re
import json
import requests

url = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)

html = response.text

match = re.search(
    r'var d=(\{.*?"staticQueryHashes":\[\].*?"slicesMap":\{\}\})',
    html,
    re.DOTALL
)

data = json.loads(match.group(1))

days = data["result"]["pageContext"]["menu"]["Days"]

print("PÄIVIÄ:", len(days))
print("ENSIMMÄINEN PÄIVÄ:")
print(days[0]["Date"])

print("ENSIMMÄINEN RUOKA:")
print(days[0]["Meals"][0]["Nutritions"][0]["Name"])

print("ENSIMMÄINEN LISUKE:")
print(days[0]["Meals"][0]["Nutritions"][1]["Name"])
