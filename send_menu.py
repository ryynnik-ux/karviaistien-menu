import requests
import re

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

print("MATCH:", match is not None)

if match:
    print("JSON_LENGTH:", len(match.group(1)))
    print(match.group(1)[:300])
