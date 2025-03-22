import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import csv

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

# Function to generate recipe using Gemini API with enhanced multimodal support
def generate_recipe(user_input, image=None):
    prompt = f"""
    You are an expert chef. Based on the following inputs, generate a detailed recipe:
    - User Input: {user_input if user_input else 'None'}
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

# Function to generate and save 25,000 recipes to CSV
def generate_bulk_recipes():
    with open("recipes.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Recipe Name", "Ingredients", "Instructions", "Cooking Time", "Serving Size"])
        
        for i in range(25000):
            user_input = f"Recipe {i+1}"  # Placeholder input
            recipe_text = generate_recipe(user_input)
            recipe_lines = recipe_text.split("\n")
            if len(recipe_lines) >= 4:
                writer.writerow([recipe_lines[0], recipe_lines[1], recipe_lines[2], recipe_lines[3], "Unknown"])

# ✅ Streamlit UI Configuration
def main():
    st.set_page_config(page_title="AI Chef Recipe Generator", layout="wide")
    st.title("🍽️ AI Chef Recipe Generator")
    st.write("Generate recipes based on your preferences or images!")

    # User Input Section
    user_input = st.text_area("Enter dietary preferences, cuisine type, or available ingredients:", height=150)

    # Image Upload Section
    uploaded_image = st.file_uploader("Upload an image of ingredients or a dish (Optional)", type=["jpg", "png", "jpeg"])
    image = Image.open(uploaded_image) if uploaded_image else None
    if image:
        st.image(image, caption="Uploaded Image", use_column_width=True)

    # Generate Recipe Button
    if st.button("Generate Recipe"):
        if not any([user_input, image]):
            st.error("Please provide at least one input (text or image).")
        else:
            with st.spinner("Generating your recipe..."):
                recipe = generate_recipe(user_input, image)
                st.subheader("Generated Recipe")
                st.markdown(recipe)
    
    # Generate 25,000 Recipes CSV Button
    if st.button("Generate 25,000 Recipes CSV"):
        with st.spinner("Generating 25,000 recipes. This may take a while..."):
            generate_bulk_recipes()
        st.success("✅ 25,000 recipes have been saved to 'recipes.csv'!")

if __name__ == "__main__":
    main()
