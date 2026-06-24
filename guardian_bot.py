import os
import re  # Added for structural text parsing and PII masking
from google import genai
from google.genai import types
from pymongo import MongoClient

# LOCAL FALLBACK CACHE
LOCAL_DATABASE_FALLBACK = {
    "Grandparent Scam": "In a grandparent scam, an emergency imposter calls claiming a grandchild is in urgent financial or legal trouble. Guardian Protocol: Instruct the user to hang up immediately and call the grandchild directly on their known, trusted number to verify. Never wire funds, send gift cards, or provide cryptocurrency tokens under high-pressure scenarios.",
    "Phishing and Spoofing Links": "Phishing text messages or emails mimic official banks, delivery services, or utility agencies to steal credentials. Guardian Protocol: Look for mismatched URLs, urgent warnings about accounts being closed, or unusual payment requests. Do not click links. Navigate to the official provider website via a clean browser window instead.",
    "Remote Access Scams": "Fraudsters pose as tech support agents claiming your computer has a virus to gain remote entry. Guardian Protocol: Legitimate tech support teams will never contact you out of the blue or demand access via software tools like AnyDesk or TeamViewer. Do not download software on unverified calls."
}


def redact_pii(text):
    """
    Automated PII Redaction Pipeline
    Scans input text using regular expressions and masks sensitive information
    before it leaves the user's environment.
    """
    if not text:
        return ""

    # 1. Mask Social Security Numbers (Formats: 000-00-0000 or 000000000)
    ssn_pattern = r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b'
    text = re.sub(ssn_pattern, "[🔒 SSN REDACTED]", text)

    # 2. Mask Credit Card Numbers (Matches standard 13-16 digit card sequences)
    cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
    text = re.sub(cc_pattern, "[🔒 CREDIT CARD REDACTED]", text)

    # 3. Mask Email Addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text = re.sub(email_pattern, "[🔒 EMAIL REDACTED]", text)

    # 4. Mask Phone Numbers (Standard North American formats)
    phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    text = re.sub(phone_pattern, "[🔒 PHONE REDACTED]", text)

    return text


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
        # Initialize Gemini Engine securely
        ai_client = genai.Client()

        # 🔒 PIPELINE STEP: Sanitize user text inputs to remove PII completely
        sanitized_text = redact_pii(user_text) if user_text else ""

        # Determine the safety protocol context based on our sanitized text hint
        safety_protocol = fetch_safety_protocol(sanitized_text)

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

        # Inject the sanitized text account if it exists
        if sanitized_text:
            contents_payload.append(f"User Written Account (Sanitized): {sanitized_text}")

        if uploaded_file:
            file_part = types.Part.from_bytes(
                data=uploaded_file.read(),
                mime_type=uploaded_file.type,
            )
            contents_payload.append(file_part)

        if voice_audio:
            audio_part = types.Part.from_bytes(
                data=voice_audio.read(),
                mime_type=voice_audio.type,
            )
            contents_payload.append(audio_part)

        # Execute Multimodal Content Generation
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents_payload,
            config={"system_instruction": system_instruction}
        )

        return response.text

    except Exception as e:
        return f"❌ Analysis interrupted. Error: {e}"