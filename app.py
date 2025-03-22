import streamlit as st
import google.generativeai as genai
import csv
from PIL import Image
import io

# ✅ Configure API Key securely
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ API Key is missing. Go to Streamlit Cloud → Settings → Secrets and add your API key.")
    st.stop()

# ✅ AI Response Generator
def get_ai_response(prompt, fallback_message="⚠️ AI response unavailable. Please try again later."):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text.strip() if hasattr(response, "text") and response.text.strip() else fallback_message
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}\n{fallback_message}"

# Function to extract data from CSV
def extract_data_from_csv(csv_file):
    csv_reader = csv.reader(io.StringIO(csv_file.getvalue().decode("utf-8")))
    data = [row for row in csv_reader]
    return "\n".join([", ".join(row) for row in data])

# Function to generate recipe using Gemini API with enhanced multimodal support
def generate_recipe(user_input, image=None, csv_text=None):
    prompt = f"""
    You are an expert chef. Based on the following inputs, generate a detailed recipe:
    - User Input: {user_input}
    - CSV Content (if provided): {csv_text if csv_text else 'None'}
    Provide a recipe that includes:
    - Ingredients list
    - Step-by-step instructions
    - Cooking time and serving size
    - Any dietary considerations mentioned in the input
    """
    
    input_data = [prompt]
    if image:
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_data = img_byte_arr.getvalue()
        input_data.append({"mime_type": "image/png", "data": img_data})
    
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(input_data)
        return response.text.strip() if hasattr(response, "text") and response.text.strip() else "⚠️ AI response unavailable."
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}\nAI response unavailable."

# ✅ Streamlit UI Configuration
def main():
    st.set_page_config(page_title="AI Chef Recipe Generator", layout="wide")
    st.title("🍽️ AI Chef Recipe Generator")
    st.write("Generate recipes based on your preferences, images, or CSV files!")

    # User Input Section
    st.header("Step 1: Enter Your Preferences")
    user_input = st.text_area(
        "Enter your dietary preferences, cuisine type, or ingredients you have (e.g., 'vegan Italian with tomatoes')",
        height=150
    )

    # Image Upload Section
    st.header("Step 2: Upload an Image (Optional)")
    uploaded_image = st.file_uploader("Upload an image of ingredients or a dish", type=["jpg", "png", "jpeg"])
    image = None
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)

    # CSV Upload Section
    st.header("Step 3: Upload a CSV File (Optional)")
    uploaded_csv = st.file_uploader("Upload a CSV file with ingredient lists or preferences", type=["csv"])
    csv_text = None
    if uploaded_csv:
        csv_text = extract_data_from_csv(uploaded_csv)
        st.write("Extracted CSV Data:")
        st.text_area("CSV Content", csv_text, height=200)

    # Generate Recipe Button
    if st.button("Generate Recipe"):
        if not user_input and not image and not csv_text:
            st.error("Please provide at least one input (text, image, or CSV).")
        else:
            with st.spinner("Generating your recipe..."):
                recipe = generate_recipe(user_input, image, csv_text)
                st.subheader("Generated Recipe")
                st.markdown(recipe)

if __name__ == "__main__":
    main()
