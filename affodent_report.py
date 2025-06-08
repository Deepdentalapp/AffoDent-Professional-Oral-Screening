from fpdf import FPDF
import tempfile
import os

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "AffoDent Dental Screening Report", ln=1, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Page " + str(self.page_no()), 0, 0, "C")

def generate_pdf_report(name, age, sex, complaint, image, output):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    pdf.cell(0, 10, f"Name: {name}", ln=1)
    pdf.cell(0, 10, f"Age: {age}", ln=1)
    pdf.cell(0, 10, f"Sex: {sex}", ln=1)
    pdf.multi_cell(0, 10, f"Chief Complaint: {complaint}")
    pdf.ln(5)

    if "boxes" in output and len(output["boxes"]) > 0:
        pdf.cell(0, 10, f"AI Findings: {len(output['boxes'])} potential issues detected.", ln=1)
    else:
        pdf.cell(0, 10, "AI Findings: No major issues detected.", ln=1)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
        image.save(tmp_img.name)
        pdf.image(tmp_img.name, x=10, w=180)
        os.unlink(tmp_img.name)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)
        with open(tmp_pdf.name, "rb") as f:
            pdf_bytes = f.read()
        os.unlink(tmp_pdf.name)

    return pdf_bytes
