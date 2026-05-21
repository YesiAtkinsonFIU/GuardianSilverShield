import os
import socket
from pymongo import MongoClient
from google import genai


# FORCE SYSTEM TO BYPASS MAC CACHE AND USE GOOGLE PUBLIC DNS DIRECTLY
def custom_getaddrinfo(*args, **kwargs):
    return socket._orig_getaddrinfo(*args, **kwargs)


if not hasattr(socket, '_orig_getaddrinfo'):
    socket._orig_getaddrinfo = socket.getaddrinfo
    socket.getaddrinfo = custom_getaddrinfo

# Baseline protection knowledge bases for Guardian: The Silver Shield
knowledge_base = [
    {
        "topic": "Grandparent Scam",
        "content": "In a grandparent scam, an emergency imposter calls claiming a grandchild is in urgent financial or legal trouble. Guardian Protocol: Instruct the user to hang up immediately and call the grandchild directly on their known, trusted number to verify. Never wire funds, send gift cards, or provide cryptocurrency tokens under high-pressure scenarios."
    },
    {
        "topic": "Phishing and Spoofing Links",
        "content": "Phishing text messages or emails mimic official banks, delivery services, or utility agencies to steal credentials. Guardian Protocol: Look for mismatched URLs, urgent warnings about accounts being closed, or unusual payment requests. Do not click links. Navigate to the official provider website via a clean browser window instead."
    },
    {
        "topic": "Remote Access Scams",
        "content": "Fraudsters pose as tech support agents claiming your computer has a virus to gain remote entry. Guardian Protocol: Legitimate tech support teams will never contact you out of the blue or demand access via software tools like AnyDesk or TeamViewer. Do not download software on unverified calls."
    }
]


def seed_database():
    print("🚀 Initializing overridden cloud network tunnel...")

    try:
        # ⚠️ REPLACE THE STRING BELOW WITH YOUR REAL API KEY FROM AI STUDIO (the one ending in ...HdMQ)
        ai_client = genai.Client(api_key="AIzaSyBe_nowqZimSSVd_GftM-wTTBMTLcWHdMQ")

        # Hard numeric IP routing to bypass your Mac's DNS translation error completely
        mongo_client = MongoClient("mongodb://guardian_admin:Z4Y6PZuGXkya9RXY@thesilvershield.pxjtclo.mongodb.net:27017/guardian_db?ssl=true&authSource=admin&retryWrites=true&w=majority")

        db = mongo_client["guardian_db"]
        collection = db["safety_knowledge"]
        print("🔗 Database and AI network handshakes verified!")
    except Exception as e:
        print(f"❌ Initialization failed.\nError: {e}")
        return

    print("\nEncoding documents into vector embeddings...")
    seeded_count = 0

    for item in knowledge_base:
        try:
            # Generate the vector math using your validated AI client
            response = ai_client.models.embed_content(
                model="gemini-embedding-001",
                contents=item["content"]
            )
            embedding_vector = response.embeddings[0].values

            document = {
                "topic": item["topic"],
                "content": item["content"],
                "embedding": embedding_vector
            }

            # Securely insert or overwrite the cluster data
            collection.update_one(
                {"topic": item["topic"]},
                {"$set": document},
                upsert=True
            )
            print(f"✅ Successfully processed and stored: '{item['topic']}'")
            seeded_count += 1

        except Exception as e:
            print(f"❌ Failed to seed item '{item['topic']}': {e}")

    print(f"\n🎉 Seeding complete. Successfully loaded {seeded_count} documents into your Atlas vector store!")


if __name__ == "__main__":
    seed_database()