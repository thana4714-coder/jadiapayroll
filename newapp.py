from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return redirect(url_for("payroll"))  # use the payroll route below

# --- Robust time parsing -----------------------------------------------
def parse_time(text: str):
    """Try multiple formats; accept things like '8:30 AM', '8am', '0830PM', '21:15'."""
    if not text:
        return None
    t = text.strip().upper().replace(".", "")  # '8.30am' -> '8 30AM' after fixes below

    # Insert a space before AM/PM if missing, e.g., '8:30AM' -> '8:30 AM'
    if t.endswith("AM") or t.endswith("PM"):
        if len(t) >= 3 and t[-3] != " ":
            t = t[:-2] + " " + t[-2:]

    # Turn bare '830 AM' into '8:30 AM'
    if (" AM" in t or " PM" in t) and ":" not in t:
        # e.g. '0830 AM' or '830 AM' -> try to split minutes
        parts = t.split()
        digits = "".join(ch for ch in parts[0] if ch.isdigit())
        ap = parts[1]
        if 3 <= len(digits) <= 4:
            h = digits[:-2]
            m = digits[-2:]
            t = f"{int(h)}:{m} {ap}"

    # Candidate formats to try (12h and 24h)
    fmts = [
        "%I:%M %p",  # 8:30 AM
        "%I %p",     # 8 AM
        "%H:%M",     # 21:15
        "%H",        # 8
    ]
    for f in fmts:
        try:
            return datetime.strptime(t, f)
        except ValueError:
            pass
    return None

def hours_between(start_str, end_str):
    s = parse_time(start_str)
    e = parse_time(end_str)
    if not s or not e:
        return None  # invalid input
    diff = (e - s).total_seconds() / 3600.0
    if diff < 0:
        diff += 24  # crossed midnight
    return round(diff, 2)

# --- Web routes ---------------------------------------------------------
@app.route("/payroll", methods=["GET", "POST"])
def payroll():
    results = []
    errors = []

    if request.method == "POST":
        for i in range(1, 5):
            start_txt = request.form.get(f"start{i}", "").strip()
            end_txt   = request.form.get(f"end{i}", "").strip()

            hrs = hours_between(start_txt, end_txt)
            if start_txt or end_txt:  # user typed something
                if hrs is None:
                    errors.append(f"Subject {i}: time format not understood ('{start_txt}' → '{end_txt}'). "
                                  f"Try 8:30 AM, 8 AM, 0830PM, or 21:15.")
                    hrs = 0.0  # still show a row
                pay15 = round(hrs * 15, 2)
                pay18 = round(hrs * 18, 2)
                results.append((f"Subject {i}", start_txt, end_txt, hrs, pay15, pay18))

    return render_template("payroll.html", results=results, errors=errors)

if __name__ == "__main__":
    # open http://127.0.0.1:5001/payroll
    app.run(debug=True, port=5001)