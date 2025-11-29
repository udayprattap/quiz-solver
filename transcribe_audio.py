import speech_recognition as sr
import httpx
import json
import asyncio

async def transcribe_and_submit():
    """Transcribe audio using Google Speech Recognition"""
    
    # Initialize recognizer
    recognizer = sr.Recognizer()
    
    # Load audio file
    with sr.AudioFile('audio-passphrase.wav') as source:
        print("Loading audio...")
        audio_data = recognizer.record(source)
        
        print("Transcribing with Google Speech Recognition...")
        try:
            # Use Google's free speech recognition
            text = recognizer.recognize_google(audio_data)
            print(f"✅ Transcribed: '{text}'")
            
            # Convert to lowercase as required
            answer = text.lower()
            print(f"Answer (lowercase): '{answer}'")
            
            # Submit to endpoint
            email = "24ds3000019@ds.study.iitm.ac.in"
            secret = "banana"
            submit_url = "https://tds-llm-analysis.s-anand.net/submit"
            stage_url = "https://tds-llm-analysis.s-anand.net/project2-audio-passphrase"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "email": email,
                    "secret": secret,
                    "url": stage_url,
                    "answer": answer
                }
                
                print(f"\n📤 Submitting to endpoint...")
                response = await client.post(submit_url, json=payload)
                result = response.json()
                
                print(f"\n📊 Result: {json.dumps(result, indent=2)}")
                
                if result.get('correct'):
                    print(f"\n🎉 ✅ STAGE 5 SOLVED!")
                    return answer
                else:
                    print(f"\n❌ Failed: {result.get('reason')}")
                    return None
                    
        except sr.UnknownValueError:
            print("❌ Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Could not request results; {e}")
            return None

if __name__ == "__main__":
    asyncio.run(transcribe_and_submit())
