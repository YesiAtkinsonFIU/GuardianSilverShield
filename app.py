import streamlit as st
from guardian_bot import analyze_multimodal_message

# Configure the web browser tab title and layout
st.set_page_config(
    page_title="Guardian: The Silver Shield",
    page_icon="🛡️",
    layout="centered"
)


# Custom clear logic that resets all file systems natively
def reset_interface():
    st.session_state["text_input"] = ""
    st.rerun()


st.title("🛡️ Guardian: The Silver Shield")
st.subheader("Your Personal AI Fraud & Scam Protection Companion")
st.markdown(
    "**Tri-County South Florida Support:** English | Español | Kreyòl Ayisyen\n\n"
    "If you received a suspicious phone call, text, email, or a letter in the mail, "
    "share it with Guardian below using whichever method is easiest for you."
)

st.markdown("---")

# 📋 METHOD 1: TEXT BOX
user_message = st.text_area(
    "📋 Option 1: Paste or type the suspicious text/email message here:",
    height=100,
    key="text_input",
    placeholder="Example: Your bank account is locked! Click this link immediately to verify..."
)

# 📸 METHOD 2: DRAG & DROP ATTACHMENTS/PHOTOS
uploaded_file = st.file_uploader(
    "📸 Option 2: Drag & drop a photo of a physical letter, screenshot, or bill:",
    type=["png", "jpg", "jpeg", "pdf"]
)

# 🗣️ METHOD 3: VOICE MEMO AUDIO INPUT
voice_audio = st.audio_input(
    "🗣️ Option 3: Press the microphone to record yourself describing a phone call you received:"
)

st.markdown("---")

# Layout: Create side-by-side buttons using columns
col1, col2 = st.columns([3, 1])

with col1:
    scan_clicked = st.button("🛡️ Scan with Guardian Core", use_container_width=True, type="primary")

with col2:
    st.button("🔄 Reset Screen", on_click=reset_interface, use_container_width=True)

# Processing Execution Loop
if scan_clicked:
    if not user_message.strip() and not uploaded_file and not voice_audio:
        st.warning("⚠️ Please provide information using at least one of the options above so Guardian can scan it.")
    else:
        with st.spinner("Guardian Core is assessing details, analyzing language, and scanning for coercion..."):
            analysis_result = analyze_multimodal_message(
                user_text=user_message,
                uploaded_file=uploaded_file,
                voice_audio=voice_audio
            )

        st.markdown("### 📋 Guardian Safety Assessment")
        st.info(analysis_result)
        st.success("✅ Assessment complete. Remember: when in doubt, hang up, delete, or ask a trusted loved one!")