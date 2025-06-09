


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

# Welcome message
st.title("AffoDent Oral Screening App")
st.markdown("Welcome to **AffoDent Professional Dental Clinic**, Panbazar, Guwahati, Assam.")
st.markdown("This app allows patients to submit their oral health concerns securely for doctor review.")

# Form
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

# Save patient session
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

# Doctor access
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

            # Clinic Header
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

            # Doctor Report
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
            # Images with space
            for img_file in pdata["images"]:
                if y < 350:
                    c.showPage()
                    y = height - 100

                image = Image.open(img_file)
                image = image.convert("RGB")
                image_io = io.BytesIO()
                image.save(image_io, format='PNG')
                image_io.seek(0)

                # Save to temp file and embed
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

import streamlit as st

# Section: Frequently Asked Questions
st.markdown("## 🦷 Frequently Asked Questions (FAQ)")

faqs = [
    ("How often should I visit the dentist?", "It is recommended to visit the dentist every 6 months for a routine check-up and cleaning."),
    ("How do I prevent cavities?", "Brush twice a day with fluoride toothpaste, floss daily, avoid sugary foods, and get regular dental checkups."),
    ("What is tooth sensitivity?", "Tooth sensitivity is pain or discomfort in teeth when exposed to hot, cold, sweet, or acidic foods and drinks."),
    ("When should I change my toothbrush?", "Every 3 to 4 months or sooner if the bristles are frayed."),
    ("Is flossing necessary?", "Yes, flossing removes plaque and food particles between teeth where a toothbrush can't reach."),
    ("Can mouthwash replace brushing?", "No, mouthwash is a supplementary oral hygiene aid and does not replace brushing and flossing."),
    ("Why does my jaw click while eating?", "It could be due to TMJ (temporomandibular joint) disorder and should be evaluated by a dentist."),
    ("Should I brush after every meal?", "Brushing twice a day is generally sufficient. If brushing after a meal, wait at least 30 minutes."),
    ("How can I treat bad breath?", "Maintain good oral hygiene, clean your tongue, stay hydrated, and visit a dentist for persistent issues."),
    ("What causes tooth discoloration?", "Causes include smoking, coffee, tea, red wine, poor oral hygiene, and certain medications."),
    # Continue adding up to 100 FAQs or loop through a larger list
]

with st.expander("Click to view FAQs"):
    for question, answer in faqs:
        st.markdown(f"**Q: {question}**")
        st.markdown(f"A: {answer}\n")

st.markdown("## 💬 Chat with AffoBot (Dental Assistant)")

# A simple chatbot using pre-defined Q&A
user_question = st.text_input("Ask your dental question:")

faq_dict = {
    "cavity": "To prevent cavities, brush twice daily, floss, and avoid sugary snacks. Regular checkups help too.",
    "tooth pain": "Tooth pain could be due to decay, fracture, or infection. Consult your dentist immediately.",
    "sensitivity": "Tooth sensitivity can be treated with desensitizing toothpaste. Avoid cold/sweet foods.",
    "bad breath": "Maintain oral hygiene, clean your tongue, and drink water. See a dentist if it persists.",
    "ulcer": "For ulcers, rinse with warm salt water and avoid spicy foods. Apply a topical gel if needed.",
    "gum bleeding": "This may indicate gingivitis. Brush gently, floss, and get a dental cleaning.",
    "teeth whitening": "Teeth whitening is safe when done professionally. Over-the-counter kits are less effective.",
    "wisdom teeth": "Wisdom tooth pain may need extraction if there's no space or infection.",
    "braces": "Braces are used to correct misaligned teeth. There are metal, ceramic, and invisible options.",
    "dentures": "Dentures are prosthetic replacements for missing teeth. They're removable and customizable."
}

if user_question:
    found = False
    for keyword, reply in faq_dict.items():
        if keyword in user_question.lower():
            st.success(reply)
            found = True
            break
    if not found:
        st.warning("Sorry, I couldn't find an answer. Please consult Dr. Deep Sharma.")

st.markdown("## 💰 Treatment Rate List at AffoDent Professional Dental Clinic")

treatment_rates = {
    "Dental Cleaning": "₹800",
    "Cavity Filling": "₹1200 - ₹2500",
    "Root Canal Treatment": "₹3000 - ₹6000",
    "Dental Crown": "₹5000 - ₹10000",
    "Tooth Extraction": "₹1000 - ₹3000",
    "Orthodontic Braces": "₹25000 - ₹75000",
    "Teeth Whitening": "₹4000 - ₹8000",
    "Dental Implants": "₹20000 - ₹45000",
    "Scaling & Polishing": "₹1000",
    "Gum Treatment": "₹2000 - ₹6000"
}

st.table(treatment_rates)
