from flask import Flask, render_template, send_from_directory
import sqlite3

app = Flask(__name__)


# 📸 Image route
@app.route('/images/<path:filename>')
def get_image(filename):
    return send_from_directory('images', filename)


# 📊 Fetch data
def get_data():
    conn = sqlite3.connect("fall_detection.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM events ORDER BY id DESC LIMIT 5"
    )

    data = cursor.fetchall()

    conn.close()

    return data


# 🟢 GET LIVE STATUS (NEW FUNCTION)
def get_live_status():
    conn = sqlite3.connect("fall_detection.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    conn.close()

    if row:
        return row[3]   # latest status

    return "Normal"

# 🏠 Dashboard
@app.route("/")
def home():

    data = get_data()
    live_status = get_live_status()   

    fall_count = 0
    recovered_count = 0
    alert_count = 0

    for row in data:

        # row[3] = status
        if row[3] == "Fall":
            fall_count += 1

        # row[6] = recovery
        if row[6] == "Recovered":
            recovered_count += 1

        # row[7] = alert
        if row[7] == "Yes":
            alert_count += 1

    return render_template(
        "index.html",
        data=data,
        fall_count=fall_count,
        recovered_count=recovered_count,
        alert_count=alert_count,
        live_status=live_status   


# 🚀 Run server
if __name__ == "__main__":
    app.run(debug=True, port=5000)