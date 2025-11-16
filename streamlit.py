# # app_streamlit_simple.py 

import streamlit as st
import os
import google.generativeai as genai
import base64
from datetime import datetime
import uuid

# ---------- For Local Image
# ---------- For Local Image (renamed clean version)
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    page_bg = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

# Call the function with new clean file name
add_bg_from_local("background.jpg")


# ---- Custom CSS for transparency and color ----
# st.markdown("""
#     <style>
#     /* ... your CSS unchanged ... */
#     </style>
# """, unsafe_allow_html=True)

st.markdown("""
<style>
h1, h3, [data-testid="stSelectbox"], p, warning {
  background: -webkit-linear-gradient(45deg, #00ffcc, #ff00cc);
  -webkit-background-clip: text;
#   -webkit-text-fill-color: transparent;
  -webkit-text-fill-color: #00ffcc;
  text-shadow: 0px 0px 10px rgba(255,255,255,0.3);
  color: #00ffcc;
  border-radius: 8px;
  padding: 8px;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="AI StreamText", layout="wide")
st.title("🤖💀  StreamText AI")

# -----------------------
# Configure API from Environment
# -----------------------
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY is not set. Add it to Streamlit Secrets or your environment variables.")
    st.stop()

genai.configure(api_key=API_KEY)


# Model choices
MODELS = {
    "gemini-2.5-flash-lite (06-17)": "models/gemini-2.5-flash-lite-preview-06-17",
    "gemini-2.5-flash (09-2025)": "models/gemini-2.5-flash-preview-09-2025"
}

# Session state for history and loaded prompt (must be set BEFORE sidebar uses it)
# if "history" not in st.session_state:
#     st.session_state.history = []  # list of {id, time, model_label, prompt, response}
# if "loaded_prompt" not in st.session_state:
#     st.session_state.loaded_prompt = ""


# Ensure session_state keys exist BEFORE sidebar uses them
if "history" not in st.session_state:
    st.session_state["history"] = []            # list of {prompt, response}
if "loaded_prompt" not in st.session_state:
    st.session_state["loaded_prompt"] = ""      # text shown in the prompt box
if "last_response" not in st.session_state:
    st.session_state["last_response"] = ""      # to persist last response across reruns



# Sidebar: model selector + history
with st.sidebar:
    st.header("Settings & History")
    selected_model_label = st.selectbox("Choose model", list(MODELS.keys()), index=1)
    model_id = MODELS[selected_model_label]

    st.markdown("---")
    st.subheader("Search history")

    if st.session_state.history:
        # show clickable prompt-only history items (latest first)
        for idx, item in enumerate(reversed(st.session_state.history)):
            prompt_preview = str(item.get("prompt", ""))[:60]  # show first 60 chars of prompt
            if st.button(prompt_preview, key=f"hist_{idx}"):
                st.session_state.loaded_prompt = str(item.get("prompt", ""))
                st.rerun()

        if st.button("🧹 Clear history"):
            st.session_state.history = []
            st.session_state.loaded_prompt = ""
            st.rerun()

    else:
        st.write("No history yet")


# Use loaded prompt if user clicked history
prompt = st.text_area("💬 Enter your prompt:", height=150, width= 500, placeholder="Ask me anything...", value=st.session_state.get("loaded_prompt", ""))

# Note: history initialization already done above; duplicate check removed (kept code minimal)

if st.button("🚀 Generate Response"):
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        try:
            # Pass the selected model id (string), not the whole MODELS dict
            model = genai.GenerativeModel(model_id)
            with st.spinner("Generating response..."):
                response = model.generate_content(prompt)
                # extract textual response defensively
                if hasattr(response, "text"):
                    text = response.text
                elif isinstance(response, dict) and "output" in response:
                    text = str(response["output"])
                else:
                    text = str(response)

                st.markdown("### 🧾 Response:")
                st.write(text)

                # Save to history with safe string coercion and metadata
                st.session_state.history.append({
                    # "id": str(uuid.uuid4()),
                    # "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "model_label": str(selected_model_label),
                    "prompt": str(prompt),
                    "response": str(text)
                })

                # clear loaded_prompt to avoid accidentally resubmitting it
                st.session_state.loaded_prompt = ""
        except Exception as e:
            st.error(f"Error: {e}")
            
# st.markdown("---")
st.markdown("""
<hr style="border: 2px solid #00ffcc; border-radius: 5px;">
""", unsafe_allow_html=True)


# st.subheader("📜 Conversation History")

# if st.session_state.history:
#     for i, h in enumerate(reversed(st.session_state.history[-10:]), 1):
#         with st.expander(f"Prompt {len(st.session_state.history) - i + 1}: {str(h.get('prompt',''))[:40]}..."):
#             st.write("*Prompt:*", h.get("prompt", ""))
#             st.write("*Response:*", h.get("response", ""))
# else:
#     st.info("No history yet. Generate a response to see history here!")

# -----------------------
# Footer
# -----------------------

st.markdown("""
<p style="text-align:center; font-weight:600; color:#00ffcc; margin:8px 0;">
  @copyright Shashank Sen
</p>
""", unsafe_allow_html=True)