# admin.py

import os
from flask import Flask, request, render_template_string, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # ברירת מחדל אם לא קיים
PORT = int(os.getenv("PORT", 8080))

client = MongoClient(MONGO_URI)
db = client["argento"]
users = db["users"]

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")

# תבנית HTML פשוטה
HTML_TEMPLATE = """
<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>🛡️ לוח ניהול – Argento X</title>
  <style>
    body { font-family: sans-serif; padding: 30px; background: #111; color: #eee; direction: rtl; }
    table { border-collapse: collapse; width: 100%; margin-top: 20px; }
    th, td { border: 1px solid #333; padding: 10px; text-align: right; }
    th { background: #222; }
    tr:nth-child(even) { background-color: #1a1a1a; }
    input { padding: 10px; font-size: 1rem; }
    .success { color: #0f0; }
    .pending { color: #ff0; }
    .new { color: #f00; }
  </style>
</head>
<body>
  {% if not authed %}
    <h2>🔐 כניסת מנהל</h2>
    <form method="post">
      <input type="password" name="password" placeholder="הכנס סיסמה">
      <button type="submit">כניסה</button>
    </form>
  {% else %}
    <h2>🧾 משתמשים רשומים – Argento X</h2>
    <table>
      <tr>
        <th>שם</th>
        <th>טלגרם ID</th>
        <th>סטטוס</th>
        <th>כתובת ETH</th>
        <th>תאריך הצטרפות</th>
      </tr>
      {% for user in users %}
      <tr>
        <td>{{ user.get("name", "לא ידוע") }}</td>
        <td>{{ user["telegram_id"] }}</td>
        <td class="{{ user['status'] }}">{{ user['status'] }}</td>
        <td>{{ user.get("eth_address", "-") }}</td>
        <td>{{ user.get("created_at", "-") }}</td>
      </tr>
      {% endfor %}
    </table>
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def admin():
    authed = False
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            authed = True
        else:
            return "❌ סיסמה שגויה", 401

    elif request.method == "GET" and request.args.get("auth") == ADMIN_PASSWORD:
        authed = True

    if authed:
        user_list = list(users.find().sort("created_at", -1))
        return render_template_string(HTML_TEMPLATE, users=user_list, authed=True)
    else:
        return render_template_string(HTML_TEMPLATE, authed=False)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
