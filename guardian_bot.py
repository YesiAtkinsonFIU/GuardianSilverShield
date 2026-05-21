import os
from google import genai
from pymongo import MongoClient

# LOCAL FALLBACK CACHE
LOCAL_DATABASE_FALLBACK = {
    "Grandparent Scam": "In a grandparent scam, an emergency imposter calls claiming a grandchild is in urgent financial or legal trouble. Guardian Protocol: Instruct the user to hang up immediately and call the grandchild directly on their known, trusted number to verify. Never wire funds, send gift cards, or provide cryptocurrency tokens under high-pressure scenarios.",
    "Phishing and Spoofing Links": "Phishing text messages or emails mimic official banks, delivery services, or utility agencies to steal credentials. Guardian Protocol: Look for mismatched URLs, urgent warnings about accounts being closed, or unusual payment requests. Do not click links. Navigate to the official provider website via a clean browser window instead.",
    "Remote Access Scams": "Fraudsters pose as tech support agents claiming your computer has a virus to gain remote entry. Guardian Protocol: Legitimate tech support teams will never contact you out of the blue or demand access via software tools like AnyDesk or TeamViewer. Do not download software on unverified calls."
}


def fetch_safety_protocol(user_text_hint):
    """Fallback keyword scanner for protocol matching."""
    user_input_lower = user_text_hint.lower() if user_text_hint else ""
    if any(word in user_input_lower for word in ["grandson", "grandchild", "arrested", "bail", "nieto"]):
        return LOCAL_DATABASE_FALLBACK["Grandparent Scam"]
    elif any(word in user_input_lower for word in ["link", "click", "bank", "banco", "locked", "clique", "lien"]):
        return LOCAL_DATABASE_FALLBACK["Phishing and Spoofing Links"]
    else:
        return LOCAL_DATABASE_FALLBACK["Remote Access Scams"]


def analyze_multimodal_message(user_text=None, uploaded_file=None, voice_audio=None):
    print("🛡️ Guardian Core active. Scanning inputs for signs of coercion...")

    try:
        # Initialize Gemini Engine securely via the unified standard client object
        ai_client = genai.Client()

        # Determine the safety protocol context based on text hint
        safety_protocol = fetch_safety_protocol(user_text)

        # SYSTEM INSTRUCTIONS: Setting the core tri-lingual persona and formatting behaviors
        system_instruction = (
            "You are Guardian, a gentle, empathetic, and deeply protective AI companion "
            "designed to shield senior citizens from fraud, scams, and high-pressure manipulation.\n\n"
            "LANGUAGE RULES FOR TRI-COUNTY SOUTH FLORIDA (Miami-Dade, Broward, Palm Beach):\n"
            "1. Detect the primary language used in the input (English, Spanish, or Haitian Creole).\n"
            "2. Respond to the user natively in that exact language (English, Spanish, or Kreyòl).\n"
            "3. Maintain your warm, comforting, and reassuring persona flawlessly across all three languages.\n\n"
            "RESPONSE FORMAT:\n"
            "Always speak directly to the user. Deconstruct the high-pressure scam tactics simply. "
            "Explicitly tell them what actions to take in a bold, clean, step-by-step format."
        )

        # Build the payload contents list dynamically for the multimodal model
        contents_payload = [
            f"Contextual Safety Rules to enforce:\n{safety_protocol}\n\n",
            "Analyze this situation and provide clear guidance."
        ]

        if user_text:
            contents_payload.append(f"User Written Account: {user_text}")

        if uploaded_file:
            # Format file data directly for Gemini's multimodal window
            file_data = {"mime_type": uploaded_file.type, "data": uploaded_file.read()}
            contents_payload.append(file_data)

        if voice_audio:
            # Format voice memo audio data directly for Gemini
            audio_data = {"mime_type": voice_audio.type, "data": voice_audio.read()}
            contents_payload.append(audio_data)

        # Execute Multimodal Content Generation
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents_payload,
            config={"system_instruction": system_instruction}
        )

        return response.text

    except Exception as e:
        return f"❌ Analysis interrupted. Error: {e}"