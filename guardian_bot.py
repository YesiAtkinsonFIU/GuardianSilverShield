import os
import re
import io
from google import genai
from google.genai import types
from pymongo import MongoClient
from PIL import Image
from pillow_heif import register_heif_opener

# ✨ Register the HEIF opener globally at startup so Pillow natively reads Apple HEIC images
register_heif_opener()

# LOCAL FALLBACK CACHE
LOCAL_DATABASE_FALLBACK = {
    "Grandparent Scam": "In a grandparent scam, an emergency imposter calls claiming a grandchild is in urgent financial or legal trouble. Guardian Protocol: Instruct the user to hang up immediately and call the grandchild directly on their known, trusted number to verify. Never wire funds, send gift cards, or provide cryptocurrency tokens under high-pressure scenarios.",
    "Phishing and Spoofing Links": "Phishing text messages or emails mimic official banks, delivery services, or utility agencies to steal credentials. Guardian Protocol: Look for mismatched URLs, urgent warnings about accounts being closed, or unusual payment requests. Do not click links. Navigate to the official provider website via a clean browser window instead.",
    "Remote Access Scams": "Fraudsters pose as tech support agents claiming your computer has a virus to gain remote entry. Guardian Protocol: Legitimate tech support teams will never contact you out of the blue or demand access via software tools like AnyDesk or TeamViewer. Do not download software on unverified calls."
}


def redact_pii(text):
    """Automated PII Redaction Pipeline"""
    if not text:
        return ""
    ssn_pattern = r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b'
    text = re.sub(ssn_pattern, "[🔒 SSN REDACTED]", text)
    cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
    text = re.sub(cc_pattern, "[🔒 CREDIT CARD REDACTED]", text)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text = re.sub(email_pattern, "[🔒 EMAIL REDACTED]", text)
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


def log_to_mongodb(session_id, sanitized_text, classification):
    """Dual-Collection Privacy Engine"""
    mongo_uri = os.environ.get("MONGO_URI")
    if not mongo_uri:
        print("⚠️ MongoDB URI missing. Simulating database write locally.")
        return False

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        db = client["guardian_shield_db"]

        db.active_sessions.insert_one({
            "session_id": session_id,
            "status": "active",
            "has_text_payload": bool(sanitized_text)
        })

        if sanitized_text:
            db.global_telemetry.insert_one({
                "threat_context": sanitized_text,
                "inferred_classification": classification
            })
        return True
    except Exception as e:
        print(f"⚠️ Database connection deferred: {e}")
        return False


def purge_session_from_db(session_id):
    """Wipes active session footprints completely."""
    mongo_uri = os.environ.get("MONGO_URI")
    if not mongo_uri:
        print("🔄 Local session cache simulation cleared successfully.")
        return True
    try:
        client = MongoClient(mongo_uri)
        db = client["guardian_shield_db"]
        db.active_sessions.delete_many({"session_id": session_id})
        print(f"🔒 GDPR Compliance: Session {session_id} permanently purged.")
        return True
    except Exception as e:
        print(f"❌ Error during data purging: {e}")
        return False


def analyze_multimodal_message(user_text=None, uploaded_files=None, voice_audio=None, session_id=None):
    """Upgraded to securely process multiple files simultaneously and intercept raw iOS HEIC formats!"""
    print("🛡️ Guardian Core active. Scanning inputs for signs of coercion...")

    try:
        ai_client = genai.Client()
        sanitized_text = redact_pii(user_text) if user_text else ""
        safety_protocol = fetch_safety_protocol(sanitized_text)

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

        contents_payload = [
            f"Contextual Safety Rules to enforce:\n{safety_protocol}\n\n",
            "Analyze this situation and provide clear guidance."
        ]

        if sanitized_text:
            contents_payload.append(f"User Written Account (Sanitized): {sanitized_text}")

        # 🎉 UPGRADE: Loop through, process, and attach all uploaded assets/photos
        if uploaded_files:
            for file in uploaded_files:
                file_name = file.name.lower()

                # 🍏 Intercept iPhone HEIC/HEIF files and translate them to a standard JPEG payload
                if file_name.endswith('.heic') or file_name.endswith('.heif'):
                    heic_image = Image.open(file)
                    bytes_io = io.BytesIO()
                    heic_image.convert("RGB").save(bytes_io, format="JPEG")
                    bytes_io.seek(0)

                    file_data = bytes_io.getvalue()
                    mime_type = "image/jpeg"
                else:
                    # Treat standard formats (PNG, JPG, PDF) normally
                    file_data = file.read()
                    mime_type = file.type

                file_part = types.Part.from_bytes(
                    data=file_data,
                    mime_type=mime_type
                )
                contents_payload.append(file_part)

        if voice_audio:
            audio_part = types.Part.from_bytes(data=voice_audio.read(), mime_type=voice_audio.type)
            contents_payload.append(audio_part)

        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents_payload,
            config={"system_instruction": system_instruction}
        )

        log_to_mongodb(session_id, sanitized_text, "Inferred Threat Scan")
        return response.text

    except Exception as e:
        return f"❌ Analysis interrupted. Error: {e}"

    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    def email_guardian_report(recipient_email, report_text):
        """
        Transports fully redacted safety protocols securely to caregivers
        utilizing corporate server credentials.
        """
        # Grab your environment variables (Set these up in your Streamlit Secrets Manager)
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        sender_email = os.environ.get("SENDER_EMAIL")  # e.g., your corporate email
        sender_password = os.environ.get("SENDER_PASSWORD")  # App Password token

        if not sender_email or not sender_password:
            print("⚠️ Outbound mail credentials missing from environment.")
            return False

        try:
            # Construct the email packet
            msg = MIMEMultipart()
            msg['From'] = f"Guardian: Silver Shield <{sender_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = "🚨 Guardian Safety Alert: Fraud Protocol Action Required"

            # Body formatting designed for instant legibility
            body = (
                "Hello,\n\n"
                "A member of your family or care circle recently scanned a potential threat "
                "using Guardian: The Silver Shield. Below is the immediate, sanitized step-by-step "
                "action protocol generated to keep them safe:\n\n"
                "============================================================\n"
                f"{report_text}\n"
                "============================================================\n\n"
                "Please reach out to them directly to provide reassurance and ensure no financial "
                "or personal data assets have been compromised.\n\n"
                "Sincerely,\n"
                "Guardian Security Operations Engine\n"
                "Managed by BYse Ventures LLC"
            )

            msg.attach(MIMEText(body, 'plain'))

            # Secure TLS Transport Connection Execution
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()

            return True
        except Exception as e:
            print(f"❌ Transactional email dispatch failure: {e}")
            return False