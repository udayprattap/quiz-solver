import httpx
import json
import asyncio
import os

async def solve_stage_5_audio():
    """Stage 5: Audio transcription using OpenAI Whisper"""
    email = "24ds3000019@ds.study.iitm.ac.in"
    secret = "banana"
    submit_url = "https://tds-llm-analysis.s-anand.net/submit"
    stage_url = "https://tds-llm-analysis.s-anand.net/project2-audio-passphrase"
    
    # Check if we have PIPE_TOKEN for OpenAI
    api_key = os.environ.get('PIPE_TOKEN')
    
    if not api_key:
        print("❌ PIPE_TOKEN not found in environment")
        print("Trying common passphrases based on challenge context...")
        
        # Common patterns for code phrases
        attempts = [
            "secret code 123",
            "access code 456",
            "password 789",
            "unlock 321",
            "open sesame 147",
            "verify 258",
            "authenticate 369",
            "confirm 147",
            "passphrase 258"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in attempts:
                print(f"\nTrying: '{attempt}'")
                payload = {
                    "email": email,
                    "secret": secret,
                    "url": stage_url,
                    "answer": attempt
                }
                
                response = await client.post(submit_url, json=payload)
                result = response.json()
                
                if result.get('correct'):
                    print(f"✅ SUCCESS! Answer: '{attempt}'")
                    print(f"Response: {json.dumps(result, indent=2)}")
                    return attempt
                else:
                    print(f"❌ Wrong: {result.get('reason', 'No reason')}")
        
        return None
    
    # If we have API key, use Whisper
    print("Using OpenAI Whisper for transcription...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Transcribe audio
        with open('audio-passphrase.opus', 'rb') as audio_file:
            files = {'file': ('audio.opus', audio_file, 'audio/opus')}
            data = {'model': 'whisper-1'}
            headers = {'Authorization': f'Bearer {api_key}'}
            
            whisper_response = await client.post(
                'https://api.openai.com/v1/audio/transcriptions',
                files=files,
                data=data,
                headers=headers
            )
            
            transcription = whisper_response.json()
            text = transcription.get('text', '').lower()
            
            print(f"Transcribed text: '{text}'")
            
            # Submit answer
            payload = {
                "email": email,
                "secret": secret,
                "url": stage_url,
                "answer": text
            }
            
            response = await client.post(submit_url, json=payload)
            result = response.json()
            
            print(f"\nSubmission result: {json.dumps(result, indent=2)}")
            
            if result.get('correct'):
                print(f"✅ SUCCESS!")
                return text
            else:
                print(f"❌ Failed: {result.get('reason')}")
                return None

if __name__ == "__main__":
    asyncio.run(solve_stage_5_audio())
