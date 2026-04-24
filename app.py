from flask import Flask, render_template, send_from_directory
import sqlite3

app = Flask(__name__)

# 📸 Image route (important for snapshots)
@app.route('/images/<path:filename>')
def get_image(filename):
    return send_from_directory('images', filename)

# 📊 Fetch data from database
def get_data():
    conn = sqlite3.connect("fall_detection.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT 5")
    data = cursor.fetchall()
    conn.close()
    return data

# 🏠 Home route (dashboard)
@app.route("/")
def home():
    return render_template("index.html", data=get_data())

# 🚀 Run server
if __name__ == "__main__":
    app.run(debug=True)