import requests

url = "https://kouluruoka.fi/menu/helsinki_karviaistienkoulu/"

response = requests.get(url, timeout=30)

print("STATUS:")
print(response.status_code)

print("\nFIRST 5000 CHARS:\n")
print(response.text[:5000])

with open("page.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("\nDONE")
