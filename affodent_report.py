from fpdf import FPDF
from io import BytesIO
import datetime

def summarize_findings(output):
    labels = output.get("labels", [])
    label_names = {
        1: "Caries",
        2: "Missing Tooth",
        3: "Broken Tooth",
        4: "Stain",
        5: "Calculus",
        6: "Ulcer",
        7: "Lesion",
        8: "Root Stamp"
    }
    summary = {}
    for label in labels:
        name = label_names.get(int(label), "Unknown")
        summary[name] = summary.get(name, 0) + 1
    return summary

def generate_pdf_report(name, age, sex, complaint, image, output):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AffoDent Dental Screening Report", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Date: {datetime.date.today()}", ln=True)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Age: {age}", ln=True)
    pdf.cell(0, 10, f"Sex: {sex}", ln=True)
    pdf.cell(0, 10, f"Chief Complaint: {complaint}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "AI Detected Findings:", ln=True)

    findings = summarize_findings(output)
    pdf.set_font("Arial", "", 12)
    if findings:
        for condition, count in findings.items():
            pdf.cell(0, 10, f"- {condition}: {count} region(s) detected", ln=True)
    else:
        pdf.cell(0, 10, "No significant findings detected.", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "AI-Marked Image:", ln=True)

    img_temp = BytesIO()
    image.save(img_temp, format="PNG")
    img_temp.seek(0)

    pdf.image(img_temp, x=10, y=pdf.get_y(), w=180)

    pdf.ln(85)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Note: This is an automated screening report and should be clinically verified.", ln=True)

    output_buffer = BytesIO()
    pdf.output(output_buffer)
    return output_buffer.getvalue()
