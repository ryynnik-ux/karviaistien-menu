import requests

url = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)

html = response.text

print("FOUND:", "gatsby-inlined-page-data" in html)

print("POSITION:")
print(html.find("gatsby-inlined-page-data"))

print("SNIPPET:")

pos = html.find("gatsby-inlined-page-data")

if pos != -1:
    print(html[pos:pos+10000])
