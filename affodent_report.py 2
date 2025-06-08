from fpdf import FPDF
import tempfile
import os

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "AffoDent Dental Screening Report", ln=1, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Page " + str(self.page_no()), 0, 0, "C")

def generate_pdf_report(name, age, sex, complaint, image, output):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 12)

    # Patient Info
    pdf.cell(0, 10, f"Name: {name}", ln=1)
    pdf.cell(0, 10, f"Age: {age}", ln=1)
    pdf.cell(0, 10, f"Sex: {sex}", ln=1)
    pdf.multi_cell(0, 10, f"Chief Complaint: {complaint}")
    pdf.ln(5)

    # AI Findings (basic example)
    findings = []
    if "boxes" in output and len(output["boxes"]) > 0:
        findings.append(f"AI detected {len(output['boxes'])} possible findings.")
    else:
        findings.append("No major issues detected.")

    pdf.multi_cell(0, 10, "Findings:\n" + "\n".join(findings))
    pdf.ln(5)

    # Save image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
        image.save(tmp_img.name)
        pdf.image(tmp_img.name, x=10, w=180)
        os.unlink(tmp_img.name)

    # Return as bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        with open(tmp_file.name, "rb") as f:
            pdf_bytes = f.read()
        os.unlink(tmp_file.name)
        return pdf_bytes
