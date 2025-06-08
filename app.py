import streamlit as st
from PIL import Image
import torch
import torchvision.transforms as T
from torchvision.models.detection import maskrcnn_resnet50_fpn
import requests
import os
from io import BytesIO
from affodent_report import generate_pdf_report

MODEL_PATH = "models/MASK_RCNN_ROOT_SEGMENTATION.pth"
MODEL_URL = "https://huggingface.co/deepdentalscan/maskrcnn/resolve/main/MASK_RCNN_ROOT_SEGMENTATION.pth"

def download_model():
    os.makedirs("models", exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        with st.spinner("Downloading AI model..."):
            response = requests.get(MODEL_URL)
            with open(MODEL_PATH, "wb") as f:
                f.write(response.content)
            st.success("Model downloaded!")

@st.cache_resource
def load_model():
    download_model()
    model = maskrcnn_resnet50_fpn(pretrained=False)
    state_dict = torch.load(MODEL_PATH, map_location="cpu")
    model.load_state_dict(state_dict)
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
    for box in output["boxes"]:
        coords = [int(x) for x in box]
        draw_crop = draw.crop(coords)
        draw.paste(draw_crop, coords)  # This is a placeholder; add annotation logic here if needed
    return draw

# Streamlit UI
st.set_page_config(page_title="AffoDent Screening App")
st.title("AffoDent Dental Screening App")

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

    st.subheader("Uploaded Image")
    st.image(image, use_column_width=True)

    annotated = draw_boxes(image, output)

    st.subheader("AI Marked Image")
    st.image(annotated, use_column_width=True)

    pdf_bytes = generate_pdf_report(name, age, sex, complaint, annotated, output)
    st.download_button("Download PDF Report", data=pdf_bytes, file_name=f"{name}_dental_report.pdf", mime="application/pdf")
