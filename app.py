import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os
import uuid

# Constants
DOCTOR_PASSWORD = "doctor123"
DATA_DIR = "data"

# Ensure directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Helper to save images
def save_uploaded_images(images, patient_id):
    image_paths = []
    for i, img in enumerate(images):
        path = os.path.join(DATA_DIR, f"{patient_id}_img_{i}.jpg")
        with open(path, "wb") as f:
            f.write(img.getbuffer())
        image_paths.append(path)
    return image_paths

# PDF Report Generator
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "AffoDent Professional Dental Clinic", ln=1, align="C")
        self.set_font("Arial", "", 10)
        self.cell(0, 8, "Dr. Deep Sharma, BDS, MDS", ln=1, align="C")
        self.cell(0, 6, "College Hostel Road, Panbazar, Guwahati, Assam", ln=1, align="C")
        self.ln(5)
        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        self.set_font("Arial", "I", 9)
        self.cell(0, 6, f"Date: {now}", ln=1, align="R")
        self.ln(5)

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_fill_color(230, 230, 250)
        self.cell(0, 8, title, ln=1, fill=True)

    def section_body(self, text):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, text)
        self.ln(4)

    def add_image(self, path):
        try:
            self.image(path, w=90)
            self.ln(5)
        except:
            self.set_font("Arial", "I", 10)
            self.cell(0, 10, f"Image error: {path}", ln=1)

    def generate(self, data, image_paths, output_path):
        self.add_page()
        self.section_title("Patient Information")
        self.section_body(f"""
Name: {data['name']}
Age: {data['age']}
Sex: {data['sex']}
WhatsApp: {data['whatsapp']}
Email: {data['email']}
        """)

        self.section_title("Chief Complaint")
        self.section_body(data["complaint"])

        self.section_title("Medical History")
        history = ", ".join(data["medical_history"]) if data["medical_history"] else "None"
        self.section_body(history)

        self.section_title("Doctor's Report")
        self.section_body(data["doctor_report"])

        self.section_title("Estimated Treatment Cost")
        self.section_body(f"Rs. {data['cost']}")

        self.section_title("Uploaded Photos")
        for img in image_paths:
            self.add_image(img)

        self.output(output_path)

# --- Streamlit App ---

st.set_page_config(page_title="AffoDent Dental Screening", layout="centered")

st.title("🦷 AffoDent Manual Dental Screening App")

st.markdown("""
#### Welcome to AffoDent Dental Screening 📸🦷  
Please fill in your details and upload oral photos for evaluation by our specialist.  
After review, you will receive a personalized dental report.
""")

# Mode switcher
mode = st.sidebar.radio("Select Mode", ["📥 Patient Upload", "🩺 Doctor Panel"])

if mode == "📥 Patient Upload":
    st.subheader("Submit Your Dental Information")

    with st.form("patient_form", clear_on_submit=True):
        name = st.text_input("Full Name", max_chars=50)
        age = st.text_input("Age", max_chars=3)
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        whatsapp = st.text_input("WhatsApp Number")
        email = st.text_input("Email Address")

        complaint = st.text_area("Chief Complaint / Dental Problem", max_chars=300)

        st.markdown("**Medical History**")
        conditions = ["Hypertension", "Diabetes", "Thyroid Problem", "Pregnancy", "Nursing Mother"]
        medical_history = [c for c in conditions if st.checkbox(c)]

        photos = st.file_uploader("Upload 2–6 Photos (Front, Side, Tongue, etc)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

        submitted = st.form_submit_button("Submit")

        if submitted:
            if not (name and age and whatsapp and email and complaint and 2 <= len(photos) <= 6):
                st.warning("Please complete all required fields and upload at least 2 images.")
            else:
                patient_id = str(uuid.uuid4())
                image_paths = save_uploaded_images(photos, patient_id)
                metadata = {
                    "name": name,
                    "age": age,
                    "sex": sex,
                    "whatsapp": whatsapp,
                    "email": email,
                    "complaint": complaint,
                    "medical_history": medical_history
                }
                with open(os.path.join(DATA_DIR, f"{patient_id}_meta.txt"), "w") as f:
                    f.write(str(metadata))
                st.success("Submitted successfully! Your report will be reviewed by the doctor.")

elif mode == "🩺 Doctor Panel":
    st.subheader("Doctor Login")
    password = st.text_input("Enter Password", type="password")
    if password == DOCTOR_PASSWORD:
        st.success("Access granted.")

        # Load all submissions
        files = [f for f in os.listdir(DATA_DIR) if f.endswith("_meta.txt")]
        if not files:
            st.info("No patient submissions found.")
        else:
            selected = st.selectbox("Select a Patient Case", files)
            with open(os.path.join(DATA_DIR, selected), "r") as f:
                data = eval(f.read())

            st.write(f"**Name**: {data['name']}")
            st.write(f"**Age**: {data['age']}, **Sex**: {data['sex']}")
            st.write(f"**WhatsApp**: {data['whatsapp']}")
            st.write(f"**Email**: {data['email']}")
            st.write(f"**Chief Complaint**: {data['complaint']}")
            st.write(f"**Medical History**: {', '.join(data['medical_history']) if data['medical_history'] else 'None'}")

            patient_id = selected.replace("_meta.txt", "")
            image_paths = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.startswith(patient_id) and f.endswith(".jpg")]

            st.markdown("**Uploaded Photos**")
            for img in image_paths:
                st.image(img, width=300)

            st.markdown("---")
            st.subheader("Write Report")

            doctor_report = st.text_area("Doctor's Report / Diagnosis", max_chars=500)
            cost = st.text_input("Approx. Treatment Cost (in Rs)", max_chars=10)

            if st.button("Generate PDF Report"):
                full_data = data.copy()
                full_data["doctor_report"] = doctor_report
                full_data["cost"] = cost

                pdf_path = os.path.join(DATA_DIR, f"{patient_id}_report.pdf")
                pdf = PDF()
                pdf.generate(full_data, image_paths, pdf_path)

                with open(pdf_path, "rb") as f:
                    st.download_button("📄 Download PDF Report", f, file_name="AffoDent_Report.pdf")

    elif password:
        st.error("Incorrect password.")
