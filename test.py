from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio configuration
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")


def test_whatsapp_connection():
    """Test WhatsApp connection with Twilio"""
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)

        # Send test message
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body='🏥 Hello! Your Healthcare Chatbot is now connected and ready to help! \n\nTry asking: "What are malaria symptoms?" or "मलेरिया के लक्षण क्या हैं?"',
            to='whatsapp:+918530231898'  # Replace with your WhatsApp number
        )

        print(f"✅ Message sent successfully!")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")

        return True

    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False


def send_test_health_queries():
    """Send test health-related queries"""
    test_queries = [
        "What are dengue symptoms?",
        "How to prevent malaria?",
        "मलेरिया के लक्षण क्या हैं?",
        "Vaccination centers near me",
        "Emergency health contacts"
    ]

    client = Client(TWILIO_SID, TWILIO_TOKEN)

    for i, query in enumerate(test_queries, 1):
        try:
            message = client.messages.create(
                from_=TWILIO_WHATSAPP_NUMBER,
                body=f"Test {i}: {query}",
                to='whatsapp:+918530231898'  # Replace with your number
            )
            print(f"✅ Test {i} sent: {message.sid}")
        except Exception as e:
            print(f"❌ Test {i} failed: {e}")


if __name__ == "__main__":
    print("🧪 Testing WhatsApp Integration...")
    print("=" * 50)

    # Test basic connection
    if test_whatsapp_connection():
        print("\n🎉 WhatsApp connection successful!")

        # Uncomment to send test queries
        # send_test_health_queries()
    else:
        print("\n❌ WhatsApp connection failed. Check your credentials.")

    print("\n📋 Next Steps:")
    print("1. Replace phone number with your actual WhatsApp number")
    print("2. Make sure you've joined Twilio WhatsApp Sandbox")
    print("3. Set up webhook URL in Twilio Console")
    print("4. Deploy your FastAPI app to get webhook URL")