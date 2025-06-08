import streamlit as st
st.set_page_config(page_title="AffoDent Dental Screening", layout="centered")

from PIL import Image
import torch
import torchvision.transforms as T
import requests
import os
from io import BytesIO
from affodent_report import generate_pdf_report

MODEL_PATH = "models/MASK_RCNN_ROOT_SEGMENTATION.pth"
MODEL_URL = "https://huggingface.co/deepdentalscan/maskrcnn/resolve/main/MASK_RCNN_ROOT_SEGMENTATION.pth"

def download_model():
    os.makedirs("models", exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        with st.spinner("Downloading model..."):
            response = requests.get(MODEL_URL)
            with open(MODEL_PATH, "wb") as f:
                f.write(response.content)
            st.success("Model downloaded.")

@st.cache_resource
def load_model():
    download_model()
    model = torch.load(MODEL_PATH, map_location="cpu")
    model.eval()
    return model

def get_prediction(model, image):
    transform = T.Compose([T.ToTensor()])
    img_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(img_tensor)[0]
    return output

def draw_boxes(image, output):
    draw = image.copy()
    return draw

st.title("AffoDent Dental Screening App")
st.write("Upload a dental image to get your AI-assisted screening report.")

with st.form("form"):
    name = st.text_input("Patient Name")
    age = st.text_input("Age")
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    complaint = st.text_area("Chief Complaint")
    submitted = st.form_submit_button("Submit")

uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_image and submitted:
    image = Image.open(uploaded_image).convert("RGB")
    model = load_model()
    output = get_prediction(model, image)

    st.image(image, caption="Uploaded Image")
    annotated = draw_boxes(image, output)
    st.image(annotated, caption="AI Marked Image")

    st.success("Analysis complete.")

    pdf_bytes = generate_pdf_report(name, age, sex, complaint, annotated, output)

    st.download_button("Download PDF Report", data=pdf_bytes, file_name=f"{name}_Dental_Report.pdf", mime="application/pdf")
