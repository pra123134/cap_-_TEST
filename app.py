import streamlit as st
import pandas as pd
import google.generativeai as genai

# ✅ Configure API Key securely
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("⚠️ API Key is missing. Go to Streamlit Cloud → Settings → Secrets and add your API key.")
    st.stop()

# ✅ Leaderboard CSV File
leaderboard_file = "leaderboard.csv"

def get_ai_response(prompt, fallback_message="⚠️ AI response unavailable. Please try again later."):
    """Handles AI response generation with error handling."""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip() if hasattr(response, "text") and response.text.strip() else fallback_message
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}\n{fallback_message}"

def extract_score(feedback):
    """Extracts the last numeric score from AI-generated feedback."""
    import re
    matches = re.findall(r'\b\d{1,2}\b', feedback)
    return int(matches[-1]) if matches else 0

def update_leaderboard(player, score):
    """Updates and saves leaderboard data to CSV securely."""
    try:
        df = pd.read_csv(leaderboard_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Player", "Score"])
    
    if player in df["Player"].values:
        df.loc[df["Player"] == player, "Score"] += max(0, score)
    else:
        df = pd.concat([df, pd.DataFrame([{ "Player": player, "Score": max(0, score) }])], ignore_index=True)
    
    df.to_csv(leaderboard_file, index=False)

def display_leaderboard():
    """Displays the leaderboard from CSV."""
    try:
        df = pd.read_csv(leaderboard_file).sort_values(by="Score", ascending=False)
        st.subheader("🏆 Leaderboard")
        st.dataframe(df)
    except FileNotFoundError:
        st.info("No leaderboard data available yet.")

# ✅ Streamlit UI
st.title("🍽️ AI-Powered Restaurant Challenge 🍽️")
player_name = st.text_input("🎮 Enter your name:", "")
if player_name:
    if st.button("Generate AI Scenario 🎲"):
        scenario = get_ai_response("Create a realistic restaurant management scenario that requires decision-making.")
        hint = get_ai_response(f"Give a short hint for handling this restaurant scenario wisely: {scenario}")
        options = get_ai_response(f"Scenario: {scenario}\n\nGenerate 4 multiple-choice response options labeled A, B, C, and D.")
        
        st.subheader("📌 AI-Generated Scenario:")
        st.write(scenario)
        st.subheader("💡 AI Hint:")
        st.write(hint)
        st.subheader("🤖 AI-Suggested Responses:")
        st.write(options)

        user_choice = st.selectbox("Choose your answer:", ["A", "B", "C", "D"])
        if st.button("Submit Answer ✅"):
            feedback = get_ai_response(f"Scenario: {scenario}\nUser's Response: {user_choice}\nProvide:\n- A brief evaluation\n- Pros and cons\n- A better alternative\n- Motivational message\n- Score from 0 to 10.")
            score = extract_score(feedback)
            
            st.subheader("🤖 AI Feedback:")
            st.write(feedback)
            st.success(f"🏅 Score: {score} Points")
            
            update_leaderboard(player_name, score)
            display_leaderboard()
else:
    st.warning("Please enter your name to start the game.")
