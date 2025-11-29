import httpx
import json
import asyncio
import math

async def solve_stage_18_v2():
    """Stage 18: Calculate minimal time - reconsidered approach"""
    email = "24ds3000019@ds.study.iitm.ac.in"
    secret = "banana"
    submit_url = "https://tds-llm-analysis.s-anand.net/submit"
    stage_url = "https://tds-llm-analysis.s-anand.net/project2-rate"
    json_url = "https://tds-llm-analysis.s-anand.net/project2/rate.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(json_url)
        c = response.json()
        
        print(f"Constraints: {json.dumps(c, indent=2)}\n")
        
        pages = c['pages']  # 1800
        per_minute = c['per_minute']  # 120
        per_hour = c['per_hour']  # 1600
        retry_after = c['retry_after_seconds']  # 30
        retry_every = c['retry_every']  # 300
        
        # Approach: Think about the limiting factor
        # At 120/min, we could do 7200 pages in an hour (way more than 1600)
        # At 1600/hour, we average 26.67/min
        # So the hourly limit is the bottleneck
        
        # Best strategy: fetch at 1600/hour pace = 26.67/min
        # This takes: 1800 / (1600/60) = 1800 / 26.67 = 67.5 minutes
        
        base_minutes_float = (pages / per_hour) * 60
        
        # Now add retry delays
        # Every 300 requests, we wait 30 seconds
        # 1800 pages = 6 batches of 300
        # So 5 retries (after batches 1,2,3,4,5 but not after the last)
        num_retries = math.floor((pages - 1) / retry_every)
        retry_minutes = (num_retries * retry_after) / 60
        
        total_minutes_float = base_minutes_float + retry_minutes
        base_minutes = math.ceil(total_minutes_float)
        
        print(f"Calculation:")
        print(f"- Pages: {pages}")
        print(f"- Hourly limit: {per_hour}/hour = {per_hour/60:.2f}/min")
        print(f"- Base time: {base_minutes_float:.2f} minutes")
        print(f"- Retries: {num_retries} * {retry_after}s = {retry_minutes:.2f} min")
        print(f"- Total: {total_minutes_float:.2f} minutes")
        print(f"- Ceiling: {base_minutes} minutes")
        
        # Add offset
        offset = len(email) % 3
        final = base_minutes + offset
        
        print(f"- Email length: {len(email)}, offset: {offset}")
        print(f"- Final answer: {final}\n")
        
        # Submit
        payload = {
            "email": email,
            "secret": secret,
            "url": stage_url,
            "answer": str(final)
        }
        
        submit_response = await client.post(submit_url, json=payload)
        result = submit_response.json()
        
        print(f"Result: {json.dumps(result, indent=2)}")
        
        if result.get('correct'):
            return result.get('url')
        else:
            # Try without ceiling
            base_minutes_2 = int(total_minutes_float)
            final_2 = base_minutes_2 + offset
            print(f"\nTrying floor instead: {base_minutes_2} + {offset} = {final_2}")
            
            payload['answer'] = str(final_2)
            submit_response = await client.post(submit_url, json=payload)
            result = submit_response.json()
            print(f"Result: {json.dumps(result, indent=2)}")
            
            if result.get('correct'):
                return result.get('url')
            
            return None

if __name__ == "__main__":
    asyncio.run(solve_stage_18_v2())
