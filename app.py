
import streamlit as st
from PIL import Image
import io
import os
import tempfile
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

st.set_page_config(page_title="AffoDent Oral Screening App", layout="wide")

# Doctor password
DOCTOR_PASSWORD = "affodoc"

# Welcome Section
st.title("AffoDent Oral Screening App")
st.markdown("Welcome to **AffoDent Professional Dental Clinic**, Panbazar, Guwahati, Assam.")
st.markdown("🦷 Upload your dental concern securely. Dr. Deep Sharma (MDS) will review and suggest treatment.")

# Patient Form
with st.form("patient_form"):
    st.header("📝 Patient Information")
    name = st.text_input("Full Name", max_chars=50)
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=1, max_value=120, step=1)
    whatsapp = st.text_input("WhatsApp Number", placeholder="Optional")
    email = st.text_input("Email Address", placeholder="Optional")
    date = st.date_input("Date of Visit", value=datetime.today())
    time = st.time_input("Time of Visit", value=datetime.now().time())
    complaint = st.text_area("Chief Complaint (Dental Problem)")

    st.subheader("Medical History (Tick if applicable)")
    hypertension = st.checkbox("Hypertension")
    diabetes = st.checkbox("Diabetes")
    thyroid = st.checkbox("Thyroid Problem")
    pregnancy = st.checkbox("Pregnant (for women)")
    nursing = st.checkbox("Nursing Mother")

    st.subheader("📸 Upload Oral Photos (2 to 6 images)")
    images = st.file_uploader("Upload Photos (Front, Left, Right, Upper, Lower, Tongue)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    submitted = st.form_submit_button("Submit")

# Save session
if submitted:
    if len(images) < 2:
        st.error("Please upload at least 2 oral photographs.")
    elif not name or not complaint:
        st.error("Please fill in all required fields (Name and Complaint).")
    else:
        st.success("Form submitted successfully. Please scroll down for doctor review.")
        st.session_state["patient_data"] = {
            "name": name,
            "sex": sex,
            "age": age,
            "whatsapp": whatsapp,
            "email": email,
            "date": str(date),
            "time": str(time),
            "complaint": complaint,
            "medical": {
                "Hypertension": hypertension,
                "Diabetes": diabetes,
                "Thyroid": thyroid,
                "Pregnancy": pregnancy,
                "Nursing": nursing
            },
            "images": images
        }

# Doctor Panel
st.divider()
st.subheader("👨‍⚕️ Doctor Panel")
doc_pass = st.text_input("Enter Doctor Password", type="password")

if doc_pass == DOCTOR_PASSWORD:
    if "patient_data" in st.session_state:
        pdata = st.session_state["patient_data"]
        st.info(f"Reviewing: {pdata['name']}, Age: {pdata['age']}, Sex: {pdata['sex']}")

        st.markdown(f"**Date & Time:** {pdata['date']} at {pdata['time']}")
        st.markdown(f"**Complaint:** {pdata['complaint']}")
        st.markdown("**Medical History:**")
        med_list = [k for k, v in pdata["medical"].items() if v]
        st.markdown(", ".join(med_list) if med_list else "None")

        st.markdown("### Uploaded Images")
        for img_file in pdata["images"]:
            st.image(img_file, width=300, caption=img_file.name)

        analysis = st.text_area("Doctor's Report / Findings")
        treatment = st.text_area("Treatment Plan and Approximate Cost")

        if st.button("Generate Report PDF"):
            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=letter)
            width, height = letter
            y = height - 50

            # Header
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "AffoDent Professional Dental Clinic")
            y -= 20
            c.setFont("Helvetica", 12)
            c.drawString(50, y, "College Hostel Road, Panbazar, Guwahati, Assam")
            y -= 30

            # Patient Info
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Patient Details")
            y -= 15
            c.setFont("Helvetica", 11)
            c.drawString(50, y, f"Name: {pdata['name']}")
            y -= 15
            c.drawString(50, y, f"Age: {pdata['age']}  Sex: {pdata['sex']}")
            y -= 15
            c.drawString(50, y, f"WhatsApp: {pdata['whatsapp'] or 'N/A'}")
            y -= 15
            c.drawString(50, y, f"Email: {pdata['email'] or 'N/A'}")
            y -= 15
            c.drawString(50, y, f"Date: {pdata['date']}  Time: {pdata['time']}")
            y -= 25
            c.drawString(50, y, f"Chief Complaint: {pdata['complaint']}")
            y -= 25
            c.drawString(50, y, "Medical History: " + (", ".join(med_list) if med_list else "None"))
            y -= 30

            # Doctor Notes
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Doctor's Findings")
            y -= 15
            c.setFont("Helvetica", 11)
            for line in analysis.splitlines():
                c.drawString(50, y, line)
                y -= 15

            y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Treatment Plan & Cost")
            y -= 15
            c.setFont("Helvetica", 11)
            for line in treatment.splitlines():
                c.drawString(50, y, line)
                y -= 15

            y -= 30
            # Embed Images
            for img_file in pdata["images"]:
                if y < 350:
                    c.showPage()
                    y = height - 100

                image = Image.open(img_file)
                image = image.convert("RGB")
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                    image.save(tmpfile.name, format="PNG")
                    c.drawImage(tmpfile.name, 50, y - 300, width=400, height=300)
                    c.drawString(50, y - 310, f"Image: {img_file.name}")
                    y -= 320

            # Footer
            c.showPage()
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 50, "Reviewed by: Dr. Deep Sharma (BDS, MDS)")
            c.save()

            st.success("✅ Report PDF generated successfully.")
            st.download_button("📄 Download Report", data=pdf_buffer.getvalue(), file_name=f"{pdata['name']}_AffoDent_Report.pdf")

else:
    if doc_pass != "":
        st.error("Incorrect password.")

# FAQ Section
st.markdown("## 🦷 Frequently Asked Questions (FAQ)")
faqs = [
    ("How often should I visit the dentist?", "Every 6 months."),
    ("How do I prevent cavities?", "Brush twice daily, floss, and avoid sugary foods."),
    ("What is tooth sensitivity?", "Discomfort when exposed to hot/cold/sweets."),
    ("Why does my jaw click while eating?", "It could be TMJ disorder."),
    ("How to treat ulcers at home?", "Use warm saltwater rinses and avoid spicy foods."),
]
with st.expander("Click to view FAQs"):
    for question, answer in faqs:
        st.markdown(f"**Q: {question}**\nA: {answer}")

# Chatbot
st.markdown("## 💬 Chat with AffoBot")
faq_dict = {
    "cavity": "Brush and floss daily, avoid sugar.",
    "ulcer": "Use saltwater rinse, apply topical gel.",
    "sensitivity": "Use desensitizing toothpaste.",
}
user_question = st.text_input("Ask a question:")
if user_question:
    matched = False
    for keyword, response in faq_dict.items():
        if keyword in user_question.lower():
            st.success(response)
            matched = True
            break
    if not matched:
        st.warning("Please consult the doctor for this query.")

# Rate List
st.markdown("## 💰 AffoDent Treatment Rate List")
treatment_rates = {
    "Dental Cleaning": "₹800",
    "Filling": "₹1200 - ₹2500",
    "RCT": "₹3000 - ₹6000",
    "Crown": "₹5000 - ₹10000",
    "Extraction": "₹1000 - ₹3000",
    "Braces": "₹25000 - ₹75000",
    "Whitening": "₹4000 - ₹8000",
    "Implants": "₹20000 - ₹45000"
}
st.table(treatment_rates)

