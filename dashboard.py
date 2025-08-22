from flask import Flask, render_template_string
import json

app = Flask(__name__)

@app.route('/')
def index():
    try:
        with open('suspects.json') as f:
            suspects = json.load(f)
    except:
        suspects = []
    try:
        with open('wifi.json') as f:
            wifi = json.load(f)
    except:
        wifi = []
    try:
        with open('temps.json') as f:
            temps = json.load(f)
    except:
        temps = []
    return render_template_string("""
    <h1>داشبورد شناسایی تجهیزات مشکوک</h1>
    <h2>خلاصه نتایج شبکه:</h2>
    <pre>{{ suspects }}</pre>
    <h2>شبکه‌های وای‌فای:</h2>
    <pre>{{ wifi }}</pre>
    <h2>دماها:</h2>
    <pre>{{ temps }}</pre>
    """, suspects=json.dumps(suspects, ensure_ascii=False, indent=2),
         wifi=json.dumps(wifi, ensure_ascii=False, indent=2),
         temps=json.dumps(temps, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)