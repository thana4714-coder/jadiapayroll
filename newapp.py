from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# ---------- Time parsing (robust) ----------
def parse_time(text: str):
    """
    Accepts '8:30 AM', '8 AM', '0830PM', '15:30', '1530', '8.30am', etc.
    Returns a datetime or None if not understood.
    """
    if not text:
        return None
    t = text.strip().upper().replace(".", "")  # '8.30am' -> '830AM'

    # Ensure a space before AM/PM if missing: '8:30AM' -> '8:30 AM'
    if t.endswith("AM") or t.endswith("PM"):
        if len(t) > 2 and t[-3] != " ":
            t = t[:-2] + " " + t[-2:]

    # If AM/PM present but no colon: '0830 AM' -> '8:30 AM'
    if (" AM" in t or " PM" in t) and ":" not in t:
        parts = t.split()
        digits = "".join(ch for ch in parts[0] if ch.isdigit())
        if len(parts) >= 2:
            ap = parts[1]
            if 3 <= len(digits) <= 4:
                h = int(digits[:-2] or "0")
                m = digits[-2:]
                t = f"{h}:{m} {ap}"

    for fmt in ("%I:%M %p", "%I %p", "%H:%M", "%H"):
        try:
            return datetime.strptime(t, fmt)
        except ValueError:
            pass
    return None

def hours_between(start_str, end_str):
    s = parse_time(start_str)
    e = parse_time(end_str)
    if not s or not e:
        return None
    diff = (e - s).total_seconds() / 3600.0
    if diff < 0:
        diff += 24  # overnight
    return round(diff, 2)

def parse_money(text: str) -> float:
    if not text:
        return 0.0
    try:
        # Allow commas/spaces
        cleaned = text.replace(",", "").strip()
        return float(cleaned)
    except:
        return 0.0

# ---------- Routes ----------
@app.route("/")
def index():
    # Redirect base URL to the form
    return redirect(url_for("payroll"))

@app.route("/payroll", methods=["GET", "POST"])
def payroll():
    results = None
    errors = []

    if request.method == "POST":
        action = request.form.get("action", "calculate").lower()
        if action == "reset":
            # Clear everything
            return redirect(url_for("payroll"))

        # One subject inputs
        start_txt = request.form.get("start", "").strip()
        end_txt   = request.form.get("end", "").strip()
        cash_txt  = request.form.get("cash_card_claim", "").strip()
        taxi_txt  = request.form.get("taxi_claim", "").strip()

        hrs = hours_between(start_txt, end_txt)
        if start_txt or end_txt:
            if hrs is None:
                errors.append(
                    f"Time not understood ('{start_txt}' → '{end_txt}'). "
                    "Try: 8:30 AM, 8 AM, 0830PM, 15:30, or 1530."
                )
                hrs = 0.0
        else:
            hrs = 0.0

        cash = parse_money(cash_txt)
        taxi = parse_money(taxi_txt)

        # Add-on claims to both pay calculations
        pay15 = round(hrs * 15 + cash + taxi, 2)
        pay18 = round(hrs * 18 + cash + taxi, 2)

        # Package results (single subject)
        results = {
        "subject": "Subject 1",
        "start": start_txt,
        "end": end_txt,
        "hours": hrs,
        "cash": round(cash, 2),
        "taxi": round(taxi, 2),
        "pay15": pay15,
        "pay18": pay18,
}

    return render_template("payroll.html", results=results, errors=errors)

# Lightweight uptime endpoint (for UptimeRobot)
@app.route("/ping")
def ping():
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
