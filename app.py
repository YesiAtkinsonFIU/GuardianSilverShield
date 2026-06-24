import streamlit as st
import uuid
from guardian_bot import analyze_multimodal_message, purge_session_from_db

# Configure the web browser tab title and layout
st.set_page_config(
    page_title="Guardian: The Silver Shield",
    page_icon="🛡️",
    layout="centered"
)

# Initialize a persistent, unique anonymous user session token if it doesn't exist
if "user_session_id" not in st.session_state:
    st.session_state["user_session_id"] = str(uuid.uuid4())


# Custom clear logic that completely wipes all text, files, and audio sessions
def reset_interface():
    # 🔒 GDPR MANDATE COMPLIANCE STEP: Trigger an immediate database wipe for the session
    purge_session_from_db(st.session_state["user_session_id"])

    # Generate a brand-new session token for the next transaction
    st.session_state["user_session_id"] = str(uuid.uuid4())

    st.session_state["text_input"] = ""
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 0
    st.session_state["uploader_key"] += 1
    if "audio_key" not in st.session_state:
        st.session_state["audio_key"] = 0
    st.session_state["audio_key"] += 1
    st.rerun()


# 🏡 TRUST-BASED WELCOME HERO SECTION
st.title("🛡️ Guardian: The Silver Shield")
st.markdown("### *Your Compassionate Protector in a Digital World*")

st.info(
    "👋 **Welcome, friend!** Guardian is a community-focused safety space designed to "
    "help you break down confusing, stressful, or high-pressure messages. "
    "Whether it's a strange phone call, an urgent text, or an unexpected bill in the mail, "
    "we are here to look at it with you and keep you safe. **Your privacy is completely protected.**"
)

with st.expander("🔍 See how Guardian safely checks your messages:"):
    st.markdown(
        "1. **Share Safely:** Share the suspicious message using whichever option below is easiest for you.\n"
        "2. **Instant Masking:** Our system scans for and redacts private information automatically.\n"
        "3. **Expert Assessment:** Guardian's AI Core checks the details against a secure database of verified scam tactics.\n"
        "4. **Step-by-Step Guidance:** You receive a clear, calm, easy-to-read safety protocol in your preferred language."
    )

st.markdown("---")
st.write("#### 🛡️ Choose how you would like to share the message with Guardian:")

# 📋 METHOD 1: TEXT BOX
user_message = st.text_area(
    "📋 Option 1: Paste or type the suspicious text/email message here:",
    height=100,
    key="text_input",
    placeholder="Example: Your bank account is locked! Click this link immediately to verify..."
)

if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0
if "audio_key" not in st.session_state:
    st.session_state["audio_key"] = 0

# 📸 METHOD 2: DRAG & DROP ATTACHMENTS
uploaded_files = st.file_uploader(
    "📸 Option 2: Drag & drop (or paste) photos of a physical letter, screenshot, or bill:",
    type=["png", "jpg", "jpeg", "pdf"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state['uploader_key']}"
)

# 🗣️ METHOD 3: VOICE MEMO AUDIO INPUT
voice_audio = st.audio_input(
    "🗣️ Option 3: Press the microphone to record yourself describing a phone call you received:",
    key=f"audio_input_{st.session_state['audio_key']}"
)

st.markdown("---")

# 📋 DISCLOSURE AND PRIVACY CONSENT CHECKBOX
st.write("#### 🔒 Final Safety Verification")
privacy_consent = st.checkbox(
    "I understand that Guardian will analyze this document securely. "
    "I authorize the system to scan this payload for hidden manipulation tactics. "
    "No personal identities or records are permanently stored."
)

st.markdown("##")

col1, col2 = st.columns([3, 1])

with col1:
    scan_clicked = st.button("🛡️ Run Secure Guardian Scan", use_container_width=True, type="primary")

with col2:
    st.button("🔄 Reset Screen", on_click=reset_interface, use_container_width=True)

# Processing Execution Loop
if scan_clicked:
    if not privacy_consent:
        st.error("⚠️ For your security, please review and check the disclosure verification box above before scanning.")
    elif not user_message.strip() and not uploaded_files and not voice_audio:
        st.warning("⚠️ Please provide information using at least one of the options above so Guardian can scan it.")
    else:
        with st.spinner(
                "Guardian Core is assessing details securely, analyzing language, and scanning for coercion..."):
            from guardian_bot import redact_pii

            visually_sanitized_text = redact_pii(user_message) if user_message else ""

            analysis_result = analyze_multimodal_message(
                user_text=user_message,
                uploaded_file=uploaded_files[0] if uploaded_files else None,
                voice_audio=voice_audio,
                session_id=st.session_state["user_session_id"]  # Pass anonymous token tracking
            )

        if user_message.strip():
            st.markdown("### 🔒 Local Privacy Shield Active")
            st.success(
                "**Data Sanitized Successfully!** To ensure your strict privacy, our automated pipeline "
                "detected and completely masked your personal credentials locally before forwarding the "
                "text context to the secure analytical engine. Here is the protected version that was evaluated:"
            )
            st.code(visually_sanitized_text, language="text")
            st.markdown("##")

        st.markdown("### 📋 Guardian Safety Assessment")
        st.info(analysis_result)
        st.success("✅ Assessment complete. Remember: when in doubt, hang up, delete, or ask a trusted loved one!")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888888; font-size: 0.85rem; padding-top: 10px;'>"
    "🛡️ Guardian: The Silver Shield™ is a proprietary solution developed by <b>BYse Ventures LLC</b>.<br>"
    "Created for the ITWomen AI for Good Challenge | © 2026 All Rights Reserved."
    "</div>",
    unsafe_allow_html=True
)