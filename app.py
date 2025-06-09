import streamlit as st
from PIL import Image
import io
import os
import tempfile
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import json
import glob

st.set_page_config(page_title="AffoDent Oral Screening App", layout="wide")

# Constants
DOCTOR_PASSWORD = "affodoc"
os.makedirs("submissions", exist_ok=True)

# Title
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
    images = st.file_uploader("Upload Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    submitted = st.form_submit_button("Submit")

if submitted:
    if len(images) < 2:
        st.error("Please upload at least 2 oral photographs.")
    elif not name or not complaint:
        st.error("Please fill in required fields (Name and Complaint).")
    else:
        # Save data
        submission_id = f"{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        save_path = os.path.join("submissions", submission_id)
        os.makedirs(save_path, exist_ok=True)

        data = {
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
            }
        }

        # Save patient data
        with open(os.path.join("submissions", f"{submission_id}.json"), "w") as f:
            json.dump(data, f, indent=4)

        # Save uploaded images
        img_dir = os.path.join("submissions", f"{submission_id}_images")
        os.makedirs(img_dir, exist_ok=True)
        for img in images:
            with open(os.path.join(img_dir, img.name), "wb") as f:
                f.write(img.read())

        st.success("✅ Submission successful! Doctor will review your case soon.")

# Doctor Login Section
with st.expander("👨‍⚕️ Doctor Login"):
    doc_pass = st.text_input("Enter Doctor Password", type="password", key="doctor_pass")

    if doc_pass == DOCTOR_PASSWORD:
        st.success("Access granted.")
        submission_files = sorted(glob.glob("submissions/*.json"), reverse=True)

        if submission_files:
            selected_file = st.selectbox("📁 Select Patient Submission", submission_files)
            if selected_file:
                with open(selected_file, "r") as f:
                    pdata = json.load(f)

                image_folder = selected_file.replace(".json", "_images")
                image_paths = glob.glob(f"{image_folder}/*")
                med_list = [k for k, v in pdata["medical"].items() if v]

                st.info(f"Reviewing: {pdata['name']}, Age: {pdata['age']}, Sex: {pdata['sex']}")
                st.markdown(f"**Date & Time:** {pdata['date']} at {pdata['time']}")
                st.markdown(f"**Complaint:** {pdata['complaint']}")
                st.markdown("**Medical History:**")
                st.markdown(", ".join(med_list) if med_list else "None")

                st.markdown("### Uploaded Images")
                for img_path in image_paths:
                    st.image(img_path, width=300, caption=os.path.basename(img_path))

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
                    for img_path in image_paths:
                        if y < 350:
                            c.showPage()
                            y = height - 100

                        image = Image.open(img_path).convert("RGB")
                        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                            image.save(tmpfile.name, format="PNG")
                            c.drawImage(tmpfile.name, 50, y - 300, width=400, height=300)
                            c.drawString(50, y - 310, f"Image: {os.path.basename(img_path)}")
                            y -= 320

                    c.showPage()
                    c.setFont("Helvetica", 12)
                    c.drawString(50, height - 50, "Reviewed by: Dr. Deep Sharma (BDS, MDS)")
                    c.save()

                    st.success("✅ Report PDF generated successfully.")
                    st.download_button("📄 Download Report", data=pdf_buffer.getvalue(), file_name=f"{pdata['name']}_AffoDent_Report.pdf")

    elif doc_pass:
        st.error("Incorrect password.")

# Optional Extras: FAQ and Rate List (unchanged from earlier)

