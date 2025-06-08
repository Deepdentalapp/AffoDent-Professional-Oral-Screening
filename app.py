import streamlit as st
from PIL import Image
import torch
import torchvision.transforms as T
import requests
from io import BytesIO
import os
from affodent_report import generate_pdf_report

# Set Streamlit page config
st.set_page_config(page_title="AffoDent Dental Screening", layout="centered")

# Constants
MODEL_PATH = "models/MASK_RCNN_ROOT_SEGMENTATION.pth"
MODEL_URL = "https://huggingface.co/deepdentalscan/maskrcnn/resolve/main/MASK_RCNN_ROOT_SEGMENTATION.pth"

# Download model if not present
def download_model():
    os.makedirs("models", exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        with st.spinner("Downloading model..."):
            response = requests.get(MODEL_URL)
            with open(MODEL_PATH, "wb") as f:
                f.write(response.content)
            st.success("Model downloaded.")

# Load model
@st.cache_resource
def load_model():
    download_model()
    model = torch.load(MODEL_PATH, map_location="cpu")
    model.eval()
    return model

# Prediction
def get_prediction(model, image):
    transform = T.Compose([T.ToTensor()])
    img_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(img_tensor)[0]
    return output

# Dummy draw function (replace with real visual logic)
def draw_boxes(image, output):
    draw = image.copy()
    return draw

# UI starts here
st.title("🦷 AffoDent Dental Screening App")

with st.form("patient_form"):
    name = st.text_input("Patient Name")
    age = st.text_input("Age")
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    complaint = st.text_area("Chief Complaint")
    submitted = st.form_submit_button("Submit")

uploaded_image = st.file_uploader("Upload a dental image", type=["jpg", "jpeg", "png"])

if uploaded_image and submitted:
    image = Image.open(uploaded_image).convert("RGB")
    model = load_model()
    output = get_prediction(model, image)

    st.image(image, caption="Uploaded Image", use_column_width=True)
    annotated = draw_boxes(image, output)
    st.image(annotated, caption="AI Marked Image", use_column_width=True)

    st.success("✅ Analysis complete.")
    st.download_button("📄 Download PDF Report",
                       generate_pdf_report(name, age, sex, complaint, annotated, output),
                       file_name=f"{name}_dental_report.pdf",
                       mime="application/pdf")
