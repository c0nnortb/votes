from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

BASE = "https://clerk.house.gov/evs/2026/"
INDEX_URL = BASE + "index.asp"

API_SECRET = "potus"

def fetch_votes(url=INDEX_URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    table = soup.find("table")
    rows = []

    if table:
        for tr in table.find_all("tr")[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if cells:
                rows.append(cells)

    df = pd.DataFrame(
        rows,
        columns=["Roll", "Date", "Issue", "Question", "Result", "Title/Description"]
    )
    return df

@app.route('/votes', methods=['GET'])
def get_votes():
    token = request.headers.get("X-API-Key")
    if token != API_SECRET:
        return jsonify({"error": "Unauthorized"}), 401

    n = request.args.get("n", 5, type=int)

    try:
        df = fetch_votes()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if df.empty:
        return jsonify({"votes": [], "count": 0})

    recent = df.head(n).to_dict(orient="records")
    return jsonify({"votes": recent, "count": len(recent)})

if __name__ == "__main__":
    app.run(port=5000)
