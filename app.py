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

leaderboard_file = "leaderboard.csv"

def get_ai_response(prompt, fallback_message="⚠️ AI response unavailable. Please try again later."):
    """Generates AI response using Gemini 1.5 Pro."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text.strip() if hasattr(response, "text") and response.text.strip() else fallback_message
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}\n{fallback_message}"

def generate_ai_scenario():
    return get_ai_response("Create a realistic restaurant management scenario that requires decision-making.")

def get_ai_suggestions(scenario):
    prompt = f"""
    Scenario: {scenario}
    Generate 4 multiple-choice response options labeled A, B, C, and D.
    Ensure the options are realistic and applicable to restaurant management.
    """
    return get_ai_response(prompt)

def get_ai_feedback(scenario, user_choice):
    prompt = f"""
    Scenario: {scenario}
    User's Response: {user_choice}

    Provide:
    - A brief evaluation of the response
    - Pros and cons of the choice
    - A better alternative if applicable
    - A motivational message if they get it right!
    - Assign a score from 0 to 10 based on correctness.
    """
    feedback = get_ai_response(prompt)
    score = extract_score(feedback)
    return feedback, score

def get_ai_hint(scenario):
    prompt = f"Give a short hint for handling this restaurant scenario wisely: {scenario}"
    return get_ai_response(prompt)

def extract_score(feedback):
    import re
    scores = [int(num) for num in re.findall(r'\b\d+\b', feedback) if 0 <= int(num) <= 10]
    return scores[-1] if scores else 0

def update_leaderboard(player, score):
    try:
        df = pd.read_csv(leaderboard_file).set_index("Player")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Player", "Score"]).set_index("Player")
    
    df.loc[player, "Score"] = df.get("Score", 0) + score
    df.reset_index().to_csv(leaderboard_file, index=False)

def display_leaderboard():
    try:
        df = pd.read_csv(leaderboard_file)
        df = df.sort_values(by="Score", ascending=False)
        st.subheader("🏆 Leaderboard 🏆")
        st.dataframe(df)
    except FileNotFoundError:
        st.info("No leaderboard data available yet.")

# ✅ Streamlit UI
st.title("🍽️ AI-Powered Restaurant Challenge 🍽️")
player_name = st.text_input("🎮 Enter your name:")

if player_name:
    if st.button("Generate AI Scenario"):
        scenario = generate_ai_scenario()
        st.subheader("📌 AI-Generated Scenario:")
        st.write(scenario)
        
        hint = get_ai_hint(scenario)
        st.info(f"💡 AI Hint: {hint}")
        
        ai_suggestions = get_ai_suggestions(scenario)
        st.subheader("🤖 AI-Suggested Responses:")
        st.write(ai_suggestions)
        
        user_choice = st.radio("Select your choice:", ["A", "B", "C", "D"])
        
        if st.button("Submit Choice"):
            ai_feedback, score = get_ai_feedback(scenario, user_choice)
            st.subheader("🤖 AI Feedback:")
            st.write(ai_feedback)
            st.success(f"🏅 Score Assigned by AI: {score} Points")
            
            update_leaderboard(player_name, score)
            display_leaderboard()
