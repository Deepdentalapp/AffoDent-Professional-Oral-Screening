import streamlit as st
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import datetime

# ---------------------------
# CONFIGURATION
# ---------------------------
DOCTOR_PASSWORD = "affodoc"
CLINIC_NAME = "AffoDent Professional Dental Clinic"
DOCTOR_NAME = "Dr. Deep Sharma, BDS, MDS"
CLINIC_ADDRESS = "College Hostel Road, Panbazar, Guwahati, Assam"
CLINIC_CONTACT = "WhatsApp: +91 9864272102"

# ---------------------------
# PAGE SETUP
# ---------------------------
st.set_page_config(page_title="AffoDent Oral Screening App", layout="centered")

st.title("🦷 AffoDent Oral Screening App")
st.markdown("Welcome to AffoDent! Upload your dental details and photos below. You will receive a professional report from Dr. Deep Sharma.")

# ---------------------------
# PATIENT FORM
# ---------------------------
with st.form("patient_form", clear_on_submit=False):
    st.subheader("Patient Information")
    name = st.text_input("Full Name", max_chars=50)
    age = st.number_input("Age", min_value=1, max_value=120, step=1)
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    whatsapp = st.text_input("WhatsApp Number (with country code)", max_chars=15)
    email = st.text_input("Email Address", max_chars=50)
    chief_complaint = st.text_area("Chief Complaint / Dental Problem", max_chars=500)
    date_time = st.date_input("Date of Submission", value=datetime.date.today())

    st.subheader("Medical History (Check if applicable)")
    hx_hypertension = st.checkbox("Hypertension")
    hx_diabetes = st.checkbox("Diabetes")
    hx_thyroid = st.checkbox("Thyroid Problem")
    hx_pregnant = st.checkbox("Pregnant (if applicable)")
    hx_nursing = st.checkbox("Nursing Mother (if applicable)")

    st.subheader("Upload Oral Photographs (Min 2 - Max 6)")
    images = st.file_uploader("Upload Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    submitted = st.form_submit_button("Submit for Review")

# Save patient submissions to session
if submitted:
    if name and len(images) >= 2:
        st.success("Data submitted. Doctor will review and send your report soon.")
        st.session_state["submission"] = {
            "name": name,
            "age": age,
            "sex": sex,
            "whatsapp": whatsapp,
            "email": email,
            "chief_complaint": chief_complaint,
            "date_time": str(date_time),
            "history": {
                "Hypertension": hx_hypertension,
                "Diabetes": hx_diabetes,
                "Thyroid": hx_thyroid,
                "Pregnant": hx_pregnant,
                "Nursing": hx_nursing
            },
            "images": images
        }
    else:
        st.error("Please fill all required fields and upload at least 2 images.")

# ---------------------------
# DOCTOR LOGIN SECTION
# ---------------------------
st.markdown("---")
st.subheader("🔐 Doctor Login to Review Submissions")

if "submission" in st.session_state:
    password = st.text_input("Enter Doctor Password", type="password")
    if password == DOCTOR_PASSWORD:
        st.success("Doctor Access Granted")
        patient_data = st.session_state["submission"]

        st.subheader(f"👤 Reviewing Patient: {patient_data['name']}")
        st.write(f"**Age/Sex**: {patient_data['age']} / {patient_data['sex']}")
        st.write(f"**WhatsApp**: {patient_data['whatsapp']}")
        st.write(f"**Email**: {patient_data['email']}")
        st.write(f"**Chief Complaint**: {patient_data['chief_complaint']}")
        st.write(f"**Date**: {patient_data['date_time']}")

        st.write("**Medical History:**")
        for k, v in patient_data["history"].items():
            if v:
                st.markdown(f"- {k}")

        # Doctor's diagnosis and notes
        st.subheader("📋 Doctor's Diagnosis & Plan")
        diagnosis = st.text_area("Diagnosis (Summary)", max_chars=500)
        treatment_plan = st.text_area("Treatment Plan", max_chars=500)
        estimated_cost = st.text_input("Estimated Cost (₹)", max_chars=20)

        # Optional: Image-wise notes
        image_notes = []
        for i, file in enumerate(patient_data["images"]):
            image = Image.open(file)
            st.image(image, caption=f"Image {i+1}", width=300)
            note = st.text_input(f"Doctor Note for Image {i+1}", key=f"note_{i}")
            image_notes.append((image, note))

        # Generate Report
        if st.button("📄 Generate PDF Report"):
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 50, CLINIC_NAME)
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, CLINIC_ADDRESS)
            c.drawString(50, height - 85, f"Doctor: {DOCTOR_NAME}")
            c.drawString(50, height - 100, f"Contact: {CLINIC_CONTACT}")
            c.line(50, height - 105, width - 50, height - 105)

            y = height - 130
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Patient Information")
            c.setFont("Helvetica", 10)
            y -= 20
            c.drawString(50, y, f"Name: {patient_data['name']}")
            y -= 15
            c.drawString(50, y, f"Age/Sex: {patient_data['age']} / {patient_data['sex']}")
            y -= 15
            c.drawString(50, y, f"Date: {patient_data['date_time']}")
            y -= 15
            c.drawString(50, y, f"WhatsApp: {patient_data['whatsapp']}")
            y -= 15
            c.drawString(50, y, f"Email: {patient_data['email']}")
            y -= 15
            c.drawString(50, y, f"Chief Complaint: {patient_data['chief_complaint']}")
            y -= 30
            c.drawString(50, y, "Medical History:")
            y -= 15
            for k, v in patient_data["history"].items():
                if v:
                    c.drawString(70, y, f"- {k}")
                    y -= 15

            y -= 15
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Doctor's Diagnosis & Plan")
            y -= 20
            c.setFont("Helvetica", 10)
            text = c.beginText(50, y)
            text.textLines(f"Diagnosis: {diagnosis}\nTreatment Plan: {treatment_plan}\nEstimated Cost: ₹{estimated_cost}")
            c.drawText(text)

            c.showPage()

            for i, (img, note) in enumerate(image_notes):
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, height - 50, f"Image {i+1}")
                c.setFont("Helvetica", 10)
                if note:
                    c.drawString(50, height - 70, f"Note: {note}")
                img = img.resize((400, 300))
                img_io = io.BytesIO()
                img.save(img_io, format="PNG")
                c.drawImage(Image.open(io.BytesIO(img_io.getvalue())), 50, height - 400, width=400, height=300)
                c.showPage()

            c.save()
            buffer.seek(0)
            st.download_button(
                label="📥 Download Report PDF",
                data=buffer,
                file_name=f"{patient_data['name'].replace(' ', '_')}_report.pdf",
                mime="application/pdf"
            )
    elif password != "":
        st.error("Incorrect password.")
else:
    st.info("No patient submission yet.")
