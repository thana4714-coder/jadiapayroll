from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

def get_hours(start, end):
    fmt = "%I:%M %p"  # 12-hour format, e.g. "09:00 AM"
    start_time = datetime.strptime(start, fmt)
    end_time = datetime.strptime(end, fmt)
    diff = (end_time - start_time).seconds / 3600
    return round(diff, 2)

@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    if request.method == "POST":
        for i in range(1, 5):
            start = request.form.get(f"start{i}")
            end = request.form.get(f"end{i}")
            if start and end:
                hours = get_hours(start, end)
                pay15 = hours * 15
                pay18 = hours * 18
                results.append((f"Subject {i}", hours, pay15, pay18))
    return render_template("payroll.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)