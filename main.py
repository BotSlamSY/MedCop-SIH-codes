from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import json
from twilio.rest import Client
from typing import Dict, Any
import os
from datetime import datetime
import asyncio
from googletrans import Translator
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Twilio Configuration
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_SANDBOX")  # Twilio sandbox number

client = Client(TWILIO_SID, TWILIO_TOKEN)
translator = Translator()

# Alternative Health APIs (Working ones)
DISEASE_API = "https://disease.sh/v3/covid-19"  # Disease.sh for COVID data
OPENWEATHER_API = "https://api.openweathermap.org/data/2.5"  # Weather affects health
NEWS_API = "https://newsapi.org/v2/everything"  # Health news

@app.post("/webhook")
async def dialogflow_webhook(request: Request):
    """Handle Dialogflow webhook requests"""
    req = await request.json()
    
    intent_name = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    parameters = req.get("queryResult", {}).get("parameters", {})
    query_text = req.get("queryResult", {}).get("queryText", "")
    
    # Detect language for multilingual support
    detected_lang = await detect_language(query_text)
    
    # Process different intents
    if intent_name == "symptoms.query":
        response = await handle_symptoms_query(parameters)
    elif intent_name == "vaccination.query":
        response = await handle_vaccination_query(parameters)
    elif intent_name == "prevention.query":
        response = await handle_prevention_query(parameters)
    elif intent_name == "health.data.query":
        response = await handle_health_data_query(parameters)
    elif intent_name == "emergency.query":
        response = await handle_emergency_query(parameters)
    else:
        response = "🏥 I'm your AI health assistant! Ask me about:\n• Disease symptoms (बीमारी के लक्षण)\n• Prevention tips (बचाव के तरीके)\n• Vaccination info (टीकाकरण जानकारी)\n• Health data (स्वास्थ्य डेटा)\n• Emergency contacts (आपातकालीन संपर्क)"
    
    # Translate response if needed
    if detected_lang == 'hi' and not any(hindi_char in response for hindi_char in ['क', 'ख', 'ग', 'घ']):
        response = await translate_text(response, 'hi')
    
    return JSONResponse({"fulfillmentText": response})

async def handle_symptoms_query(parameters: Dict) -> str:
    """Handle symptom-related queries with comprehensive disease info"""
    disease = parameters.get("disease", "").lower()
    
    symptoms_db = {
        "malaria": {
            "english": """🦟 MALARIA SYMPTOMS:
• High fever (101-104°F) with chills
• Severe headache and body aches  
• Nausea, vomiting, diarrhea
• Sweating and fatigue
• Abdominal pain
• Muscle pain

⚠️ SEEK IMMEDIATE MEDICAL ATTENTION if you have these symptoms!""",
            "hindi": """🦟 मलेरिया के लक्षण:
• तेज़ बुखार (101-104°F) ठंड के साथ
• गंभीर सिरदर्द और शरीर में दर्द
• जी मिचलाना, उल्टी, दस्त
• पसीना और थकान
• पेट में दर्द
• मांसपेशियों में दर्द

⚠️ तुरंत डॉक्टर से संपर्क करें!"""
        },
        "dengue": {
            "english": """🦟 DENGUE SYMPTOMS:
• High fever (104°F) for 3-7 days
• Severe headache (frontal headache)
• Pain behind eyes (retro-orbital pain)
• Muscle and joint pain
• Skin rash (appears 3-5 days after fever)
• Nausea and vomiting
• Easy bruising

⚠️ Watch for WARNING SIGNS: Persistent vomiting, severe abdominal pain, difficulty breathing""",
            "hindi": """🦟 डेंगू के लक्षण:
• तेज़ बुखार (104°F) 3-7 दिन तक
• गंभीर सिरदर्द (माथे में दर्द)
• आंखों के पीछे दर्द
• मांसपेशियों और जोड़ों में दर्द
• त्वचा पर दाने (बुखार के 3-5 दिन बाद)
• जी मिचलाना और उल्टी
• आसानी से नील पड़ना

⚠️ चेतावनी के संकेत: लगातार उल्टी, पेट में तेज़ दर्द"""
        },
        "covid": {
            "english": """😷 COVID-19 SYMPTOMS:
• Fever or chills
• Dry cough
• Shortness of breath
• Fatigue
• Body aches
• Loss of taste or smell
• Sore throat
• Congestion or runny nose
• Nausea or vomiting
• Diarrhea

⚠️ EMERGENCY SIGNS: Difficulty breathing, persistent chest pain, confusion""",
            "hindi": """😷 कोविड-19 के लक्षण:
• बुखार या ठंड लगना
• सूखी खांसी
• सांस लेने में कठिनाई
• थकान
• शरीर में दर्द
• स्वाद या गंध का चले जाना
• गले में खराश
• नाक बंद या बहना
• जी मिचलाना या उल्टी
• दस्त

⚠️ आपातकालीन संकेत: सांस लेने में तकलीफ, सीने में दर्द"""
        },
        "typhoid": {
            "english": """🦠 TYPHOID SYMPTOMS:
• Prolonged fever (102-104°F)
• Severe headache
• Weakness and abdominal pain
• Constipation or diarrhea
• Rose-colored rash on chest
• Loss of appetite

⚠️ Typhoid requires immediate antibiotic treatment!""",
            "hindi": """🦠 टाइफाइड के लक्षण:
• लंबे समय तक बुखार (102-104°F)
• तेज़ सिरदर्द
• कमजोरी और पेट दर्द
• कब्ज या दस्त
• छाती पर गुलाबी रंग के धब्बे
• भूख न लगना

⚠️ टाइफाइड का तुरंत इलाज जरूरी!"""
        }
    }
    
    if disease in symptoms_db:
        return f"{symptoms_db[disease]['english']}\n\n{symptoms_db[disease]['hindi']}\n\n📞 Emergency Helpline: 102 (India)"
    
    return "I can provide symptom information for: Malaria, Dengue, COVID-19, Typhoid. Which disease would you like to know about?"

async def handle_prevention_query(parameters: Dict) -> str:
    """Handle prevention-related queries"""
    disease = parameters.get("disease", "").lower()
    
    prevention_db = {
        "malaria": """🛡️ MALARIA PREVENTION:
🏠 HOME PROTECTION:
• Use mosquito nets (treated with insecticide)
• Install window/door screens
• Use mosquito repellent creams/sprays
• Wear long-sleeved clothes after sunset

🌊 ELIMINATE BREEDING SITES:
• Remove stagnant water from containers
• Clean water tanks weekly
• Cover water storage properly
• Maintain clean surroundings

💊 MEDICAL PREVENTION:
• Take antimalarial medication if traveling
• Consult doctor for prophylaxis

मलेरिया से बचाव:
• मच्छरदानी का उपयोग करें
• रुके हुए पानी को हटाएं
• शाम के बाद पूरे कपड़े पहनें""",
        
        "dengue": """🛡️ DENGUE PREVENTION:
🏠 AEDES MOSQUITO CONTROL:
• Remove all stagnant water sources
• Change water in coolers/vases weekly
• Cover all water containers
• Clean roof gutters regularly

🕐 TIME-BASED PROTECTION:
• Aedes bites during daytime
• Use repellent during day hours
• Wear full sleeves in morning/evening

🧹 COMMUNITY ACTION:
• Report breeding sites to authorities
• Participate in community cleaning drives
• Educate neighbors about prevention

डेंगू से बचाव:
• रुका हुआ पानी साफ करें
• दिन में मच्छर भगाने वाली दवा लगाएं
• पानी के बर्तन ढंक कर रखें""",
        
        "covid": """🛡️ COVID-19 PREVENTION:
😷 PERSONAL PROTECTION:
• Wear well-fitted masks in public
• Maintain 6 feet social distance
• Avoid crowded places
• Stay home when sick

🧼 HYGIENE PRACTICES:
• Wash hands for 20 seconds frequently
• Use alcohol-based sanitizer (60%+ alcohol)
• Don't touch face with unwashed hands
• Clean and disinfect surfaces

💉 VACCINATION:
• Get vaccinated and boosted
• Complete full vaccination course
• Follow local vaccination guidelines

🏠 INDOOR AIR:
• Ensure good ventilation
• Use air purifiers if possible
• Open windows for fresh air

कोविड-19 से बचाव:
• मास्क पहनें
• 6 फीट की दूरी बनाए रखें
• 20 सेकंड तक हाथ धोएं
• टीकाकरण कराएं"""
    }
    
    if disease in prevention_db:
        return prevention_db[disease]
    
    return "I can provide prevention tips for: Malaria, Dengue, COVID-19. Which disease prevention would you like to know about?"

async def handle_vaccination_query(parameters: Dict) -> str:
    """Handle vaccination-related queries with current info"""
    location = parameters.get("location", "")
    
    response = f"""💉 VACCINATION INFORMATION:

🏥 WHERE TO GET VACCINATED:
• Government Hospitals
• Primary Health Centers (PHC)
• Community Health Centers (CHC)
• Private Hospitals (authorized)
• Urban Health Centers

📋 AVAILABLE VACCINES:
• COVID-19: Free at government centers
• Hepatitis B: Available at PHCs
• Typhoid: Recommended for high-risk areas
• Japanese Encephalitis: In endemic areas

📱 HOW TO BOOK:
• Visit nearest health center directly
• Call local PHC for appointment
• Check with ASHA workers in your area

📞 HELPLINES:
• National: 1075
• State Health Dept: Check local numbers
• Emergency: 102

टीकाकरण की जानकारी:
• नजदीकी सरकारी अस्पताल में जाएं
• प्राथमिक स्वास्थ्य केंद्र (PHC) में संपर्क करें
• आशा कार्यकर्ता से बात करें

💡 Need help finding centers near you? Share your city/district name!"""
    
    return response

async def handle_health_data_query(parameters: Dict) -> str:
    """Handle health data queries using working APIs"""
    location = parameters.get("location", "india")
    
    try:
        # Get COVID data from disease.sh (working alternative)
        covid_response = requests.get(f"{DISEASE_API}/countries/{location}")
        
        if covid_response.status_code == 200:
            data = covid_response.json()
            
            response = f"""📊 HEALTH DATA FOR {location.upper()}:

🦠 COVID-19 STATUS:
• Total Cases: {data.get('cases', 'N/A'):,}
• Active Cases: {data.get('active', 'N/A'):,}
• Recovered: {data.get('recovered', 'N/A'):,}
• Today's Cases: {data.get('todayCases', 'N/A'):,}
• Vaccination Doses: {data.get('tests', 'N/A'):,}

📈 TREND:
• Cases Per Million: {data.get('casesPerOneMillion', 'N/A'):,}
• Tests Per Million: {data.get('testsPerOneMillion', 'N/A'):,}

🏥 HEALTHCARE CAPACITY:
• Critical Cases: {data.get('critical', 'N/A'):,}
• Population: {data.get('population', 'N/A'):,}

⚠️ Stay updated with local health department guidelines!
📱 Download Aarogya Setu app for latest updates

स्वास्थ्य डेटा अपडेट:
• कुल मामले: {data.get('cases', 'N/A'):,}
• सक्रिय मामले: {data.get('active', 'N/A'):,}
• ठीक हुए: {data.get('recovered', 'N/A'):,}"""
            
            return response
            
    except Exception as e:
        return f"Unable to fetch current health data. Please check local health department websites or contact helpline 1075."

async def handle_emergency_query(parameters: Dict) -> str:
    """Handle emergency contact queries"""
    return """🚨 EMERGENCY HEALTH CONTACTS:

🏥 NATIONAL EMERGENCY NUMBERS:
• Medical Emergency: 102
• Ambulance Service: 108
• National Helpline: 1075
• Women Helpline: 1091
• Child Helpline: 1098

🦠 COVID-19 HELPLINES:
• National COVID Helpline: +91-11-23978046
• Ayush Ministry: 14443

🏨 IMMEDIATE ACTION:
• Call 102 for medical emergency
• Visit nearest hospital emergency ward
• Contact local police: 100 (if needed)

🩺 POISON CONTROL:
• All India Institute: 011-26588663
• Delhi Poison Info: 011-26589391

📍 STATE-WISE HELPLINES:
• Maharashtra: 020-26127394
• Delhi: 011-22307145
• Karnataka: 080-46848600
• Tamil Nadu: 044-29510500

आपातकालीन संपर्क:
• मेडिकल इमरजेंसी: 102
• एम्बुलेंस: 108
• राष्ट्रीय हेल्पलाइन: 1075

💡 Save these numbers in your phone for quick access!"""

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    form_data = await request.form()
    
    from_number = form_data.get("From", "")
    message_body = form_data.get("Body", "")
    
    # Process with our simplified NLP (since Dialogflow webhook is set up)
    response = await process_with_simple_nlp(message_body)
    
    # Send response back via WhatsApp
    try:
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=response,
            to=from_number
        )
        return {"status": "success", "message_sid": message.sid}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def process_with_simple_nlp(text: str) -> str:
    """Simple NLP processing for direct WhatsApp integration"""
    text_lower = text.lower()
    
    # Symptom queries
    if any(word in text_lower for word in ["symptom", "लक्षण", "बीमारी", "disease"]):
        if "malaria" in text_lower or "मलेरिया" in text:
            return await handle_symptoms_query({"disease": "malaria"})
        elif "dengue" in text_lower or "डेंगू" in text:
            return await handle_symptoms_query({"disease": "dengue"})
        elif "covid" in text_lower or "कोविड" in text:
            return await handle_symptoms_query({"disease": "covid"})
        else:
            return await handle_symptoms_query({})
    
    # Prevention queries
    elif any(word in text_lower for word in ["prevent", "prevention", "बचाव", "रोकथाम"]):
        if "malaria" in text_lower or "मलेरिया" in text:
            return await handle_prevention_query({"disease": "malaria"})
        elif "dengue" in text_lower or "डेंगू" in text:
            return await handle_prevention_query({"disease": "dengue"})
        elif "covid" in text_lower or "कोविड" in text:
            return await handle_prevention_query({"disease": "covid"})
        else:
            return await handle_prevention_query({})
    
    # Vaccination queries
    elif any(word in text_lower for word in ["vaccin", "टीका", "immuniz"]):
        return await handle_vaccination_query({})

    
    # Default greeting
    else:
        return """🏥 नमस्ते! I'm your AI Health Assistant!

I can help you with:
• Disease symptoms (बीमारी के लक्षण)
• Prevention tips (बचाव के तरीके) 
• Vaccination info (टीकाकरण)
• Health data (स्वास्थ्य डेटा)
• Emergency contacts (आपातकालीन संपर्क)

Just ask me anything like:
"What are dengue symptoms?" or "मलेरिया से कैसे बचें?"

🌟 Type "help" anytime for assistance!"""

async def detect_language(text: str) -> str:
    """Detect language of input text"""
    try:
        detection = translator.detect(text)
        return detection.lang
    except:
        return 'en'  # Default to English

async def translate_text(text: str, target_lang: str = 'hi') -> str:
    """Translate text to target language"""
    try:
        # Skip translation if text already contains Hindi characters
        if any(ord(char) >= 2304 and ord(char) <= 2431 for char in text):
            return text
        
        result = translator.translate(text, dest=target_lang)
        return result.text
    except:
        return text  # Return original if translation fails

# Health monitoring background task
async def monitor_health_trends():
    """Monitor health trends and send alerts if needed"""
    while True:
        try:
            # Check for significant health trends
            response = requests.get(f"{DISEASE_API}/countries/india")
            if response.status_code == 200:
                data = response.json()
                today_cases = data.get('todayCases', 0)
                
                # Simple threshold-based alerting
                if today_cases > 10000:  # Adjust threshold as needed
                    alert_message = f"""🚨 HEALTH ALERT 🚨
                    
High number of COVID cases reported today: {today_cases:,}

Please follow safety guidelines:
• Wear masks in public
• Maintain social distancing  
• Get vaccinated
• Wash hands frequently

Stay safe! 🙏"""
                    
                    # Here you would send to registered users
                    print(f"Alert triggered: {today_cases} cases")
            
            # Check every 6 hours
            await asyncio.sleep(21600)
            
        except Exception as e:
            print(f"Health monitoring error: {e}")
            await asyncio.sleep(3600)  # Retry in 1 hour

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(monitor_health_trends())

@app.get("/")
async def root():
    return {"message": "Healthcare Chatbot API is running!", "version": "1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)