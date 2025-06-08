import streamlit as st
from PIL import Image
import torch
import torchvision.transforms as T
import torchvision.models.detection
import requests
import os
from io import BytesIO
from affodent_report import generate_pdf_report

# Model details
MODEL_PATH = "models/MASK_RCNN_ROOT_SEGMENTATION.pth"
MODEL_URL = "https://huggingface.co/deepdentalscan/maskrcnn/resolve/main/MASK_RCNN_ROOT_SEGMENTATION.pth"

# Download model from HuggingFace if not present
def download_model():
    os.makedirs("models", exist_ok=True)
    if not os.path.exists(MODEL_PATH):
        with st.spinner("Downloading AI model..."):
            response = requests.get(MODEL_URL)
            with open(MODEL_PATH, "wb") as f:
                f.write(response.content)
            st.success("Model downloaded successfully.")

# Load the model properly by rebuilding its architecture
@st.cache_resource
def load_model():
    download_model()
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(weights=None)
    state_dict = torch.load(MODEL_PATH, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()
    return model

# Get prediction
def get_prediction(model, image):
    transform = T.Compose([T.ToTensor()])
    img_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(img_tensor)[0]
    return output

# Draw bounding boxes (optional customization)
def draw_boxes(image, output):
    draw = image.copy()
    for box in output["boxes"]:
        coords = [int(x) for x in box]
        draw_crop = draw.crop(coords)
        draw.paste(draw_crop, coords)  # placeholder effect
    return draw

# -------------------- Streamlit App UI --------------------

st.set_page_config(page_title="AffoDent Dental Screening", layout="centered")
st.title("🦷 AffoDent Dental Screening App")

# Patient Details Form
with st.form("patient_form"):
    name = st.text_input("Patient Name")
    age = st.text_input("Age")
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])
    complaint = st.text_area("Chief Complaint")
    submitted = st.form_submit_button("Submit")

uploaded_image = st.file_uploader("📷 Upload a dental image", type=["jpg", "jpeg", "png"])

# Process on submit
if uploaded_image and submitted:
    image = Image.open(uploaded_image).convert("RGB")

    st.info("Analyzing image using AI...")
    model = load_model()
    output = get_prediction(model, image)

    st.image(image, caption="Original Image", use_column_width=True)
    annotated = draw_boxes(image, output)
    st.image(annotated, caption="AI Analysis Result", use_column_width=True)

    # Generate and download PDF report
    st.success("✅ Analysis complete.")
    pdf_bytes = generate_pdf_report(name, age, sex, complaint, annotated, output)
    st.download_button("📄 Download PDF Report",
                       data=pdf_bytes,
                       file_name=f"{name}_Dental_Report.pdf",
                       mime="application/pdf")
