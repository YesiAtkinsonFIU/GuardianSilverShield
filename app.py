import streamlit as st
# Import the backend reasoning engine we built and tested
from guardian_bot import analyze_message_with_context

# Configure the web browser tab title and layout
st.set_page_config(
    page_title="Guardian: The Silver Shield",
    page_icon="🛡️",
    layout="centered"
)

# Initialize the message tracking state if it doesn't exist yet
if "scam_input" not in st.session_state:
    st.session_state["scam_input"] = ""


def reset_interface():
    """Clear the text area and reset the application state."""
    st.session_state["scam_input"] = ""


# ACCESSIBLE UI DESIGN: Large, bold, high-contrast headings for readability
st.title("🛡️ Guardian: The Silver Shield")
st.subheader("Your Personal AI Fraud & Scam Protection Companion")
st.markdown(
    "If you received a suspicious phone call, text message, or email, "
    "paste the details below. Guardian will check it for hidden manipulation tactics."
)

st.markdown("---")

# Large text input box tied directly to Streamlit's session memory wrapper
user_message = st.text_area(
    "📋 Paste or type the suspicious message here:",
    height=150,
    key="scam_input",  # This binds the text area to our session state tracker
    placeholder="Example: Your bank account is locked! Click this link immediately to verify..."
)

# Layout: Create side-by-side buttons using columns
col1, col2 = st.columns([3, 1])

with col1:
    # Main action button
    scan_clicked = st.button("🛡️ Scan with Guardian Core", use_container_width=True, type="primary")

with col2:
    # Reset button that triggers our clearing function
    st.button("🔄 Reset", on_click=reset_interface, use_container_width=True)

# Process the text input if the user clicked the main scan button
if scan_clicked:
    if user_message.strip() == "":
        st.warning("⚠️ Please paste a message first so Guardian can analyze it.")
    else:
        # Show a calming loading spinner while Gemini processes the text
        with st.spinner("Scanning input for signs of coercion and high-pressure manipulation..."):
            # Call your validated reasoning engine
            analysis_result = analyze_message_with_context(user_message)

        st.markdown("### 📋 Guardian Safety Assessment")

        # Display the result inside a clean, structured information card
        st.info(analysis_result)

        st.success("✅ Assessment complete. Remember: when in doubt, hang up or delete the message!")