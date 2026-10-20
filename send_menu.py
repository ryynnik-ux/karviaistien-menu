import requests
from bs4 import BeautifulSoup

url = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

script = soup.find("script", {"id": "gatsby-inlined-page-data"})

if script:
    print("FOUND SCRIPT")
    print(script.text[:10000])
else:
    print("SCRIPT NOT FOUND")
