# ============================================================
# utils.py - Utility / Helper Functions
# ============================================================

import os

# Allowed image extensions for upload
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}

def allowed_file(filename: str) -> bool:
    """Return True if the filename has an allowed image extension."""
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)


def generate_pdf_report(record: dict, output_path: str) -> str:
    """
    Generate a simple PDF report for a prediction record.
    Uses reportlab if available, otherwise creates a plain-text file.
    Returns the path to the generated file.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors

        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # Title
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor("#1a1a2e"))
        c.drawString(50, height - 80, "AI Food Calorie Estimator")
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.grey)
        c.drawString(50, height - 100, "Prediction Report")

        # Divider
        c.setStrokeColor(colors.HexColor("#e94560"))
        c.setLineWidth(2)
        c.line(50, height - 115, width - 50, height - 115)

        # Content
        c.setFont("Helvetica", 13)
        c.setFillColor(colors.black)
        y = height - 150
        fields = [
            ("Food Name",    record.get("food_name", "—")),
            ("Calories",     f"{record.get('calories', 0)} kcal"),
            ("Protein",      f"{record.get('protein', 0)} g"),
            ("Carbohydrates",f"{record.get('carbs', 0)} g"),
            ("Fat",          f"{record.get('fat', 0)} g"),
            ("Confidence",   f"{record.get('confidence', 0)}%"),
            ("Date/Time",    record.get("timestamp", "—")),
        ]
        for label, value in fields:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(60, y, f"{label}:")
            c.setFont("Helvetica", 12)
            c.drawString(220, y, str(value))
            y -= 28

        # Health tip
        tip = record.get("health_tip", "")
        if tip:
            y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(60, y, "Health Tip:")
            y -= 20
            c.setFont("Helvetica", 11)
            # Word-wrap the tip at ~80 chars
            words = tip.split()
            line = ""
            for word in words:
                if len(line + word) < 80:
                    line += word + " "
                else:
                    c.drawString(60, y, line.strip())
                    y -= 16
                    line = word + " "
            if line:
                c.drawString(60, y, line.strip())

        c.save()
        return output_path

    except ImportError:
        # Fallback: plain text
        txt_path = output_path.replace('.pdf', '.txt')
        with open(txt_path, 'w') as f:
            f.write("AI Food Calorie Estimator - Prediction Report\n")
            f.write("=" * 50 + "\n")
            for k, v in record.items():
                f.write(f"{k}: {v}\n")
        return txt_path


def format_timestamp(ts: str) -> str:
    """Convert 'YYYY-MM-DD HH:MM:SS' to a friendlier format."""
    try:
        from datetime import datetime
        dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%d %b %Y, %I:%M %p')
    except Exception:
        return ts


def calorie_status(total_calories: float, goal: float = 2000) -> dict:
    """
    Returns a status message based on daily calorie intake vs goal.
    Default daily goal: 2000 kcal.
    """
    pct = (total_calories / goal) * 100
    if pct < 50:
        return {"status": "Under-eating", "color": "#3498db", "icon": "📉"}
    elif pct <= 90:
        return {"status": "On Track", "color": "#2ecc71", "icon": "✅"}
    elif pct <= 110:
        return {"status": "Near Goal", "color": "#f39c12", "icon": "⚠️"}
    else:
        return {"status": "Over Limit", "color": "#e74c3c", "icon": "🔴"}
