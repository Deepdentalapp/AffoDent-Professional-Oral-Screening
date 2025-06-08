from fpdf import FPDF
from PIL import Image
import io

def generate_pdf_report(name, age, sex, complaint, image, output):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="AffoDent Dental Screening Report", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
    pdf.cell(200, 10, txt=f"Age: {age}    Sex: {sex}", ln=True)
    pdf.multi_cell(200, 10, txt=f"Chief Complaint: {complaint}")

    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Findings (from AI model):", ln=True)

    labels = output.get("labels", [])
    scores = output.get("scores", [])
    for idx, label in enumerate(labels):
        if scores[idx] > 0.5:
            pdf.cell(200, 8, txt=f"- Label {label} (Confidence: {scores[idx]:.2f})", ln=True)

    # Image to PDF
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    pdf.image(img_buffer, x=10, y=pdf.get_y() + 10, w=180)

    output_buffer = io.BytesIO()
    pdf.output(output_buffer)
    output_buffer.seek(0)
    return output_buffer
