import httpx
import json
import asyncio
import math

async def solve_stage_18():
    """Stage 18: Calculate minimal time to fetch all pages with rate limiting"""
    email = "24ds3000019@ds.study.iitm.ac.in"
    secret = "banana"
    submit_url = "https://tds-llm-analysis.s-anand.net/submit"
    stage_url = "https://tds-llm-analysis.s-anand.net/project2-rate"
    json_url = "https://tds-llm-analysis.s-anand.net/project2/rate.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Download the constraints
        print("Downloading rate.json...")
        response = await client.get(json_url)
        constraints = response.json()
        
        print(f"Constraints: {json.dumps(constraints, indent=2)}")
        
        pages = constraints['pages']
        per_minute = constraints['per_minute']
        per_hour = constraints['per_hour']
        retry_after_seconds = constraints['retry_after_seconds']
        retry_every = constraints['retry_every']
        
        print(f"\nAnalysis:")
        print(f"- Total pages: {pages}")
        print(f"- Rate limits: {per_minute}/min, {per_hour}/hour")
        print(f"- Retry: every {retry_every} requests, wait {retry_after_seconds}s")
        
        # Calculate fetching strategy more carefully
        # We need to fetch 1800 pages
        # Constraint 1: max 120 per minute
        # Constraint 2: max 1600 per hour
        # Every 300 requests, we hit a retry and must wait 30 seconds
        
        print("\nCalculating optimal fetch time:")
        
        # The hourly limit is 1600 requests/hour
        # At 1600 per hour, that's 26.67 per minute (less than 120/min limit)
        # So hourly limit is the bottleneck
        
        # Number of full hours needed
        full_hours = pages // per_hour  # 1800 // 1600 = 1
        remaining_after_hours = pages % per_hour  # 1800 % 1600 = 200
        
        print(f"- Full hours: {full_hours} (fetching {full_hours * per_hour} pages)")
        print(f"- Remaining pages: {remaining_after_hours}")
        
        # Time for full hours (in minutes)
        time_full_hours = full_hours * 60
        
        # Time for remaining pages (at 120/min rate)
        time_remaining = math.ceil(remaining_after_hours / per_minute)
        
        print(f"- Time for full hours: {time_full_hours} minutes")
        print(f"- Time for remaining: {time_remaining} minutes")
        
        # Calculate retry delays
        # We hit retry every 300 requests
        num_retries = (pages - 1) // retry_every  # Don't count if we end exactly at multiple
        retry_time = (num_retries * retry_after_seconds) / 60  # convert to minutes
        
        print(f"- Number of retries: {num_retries}")
        print(f"- Retry delays: {retry_time:.2f} minutes")
        
        # Total time
        total_time = time_full_hours + time_remaining + retry_time
        base_minutes = math.ceil(total_time)
        
        print(f"\nTotal time calculation:")
        print(f"- Total time: {total_time:.2f} minutes")
        print(f"- Rounded up: {base_minutes} minutes")
        
        # Add personalized offset
        email_length = len(email)
        offset = email_length % 3
        
        final_answer = base_minutes + offset
        
        print(f"\nPersonalization:")
        print(f"- Email length: {email_length}")
        print(f"- Offset: {offset}")
        print(f"- Final answer: {final_answer}")
        
        answer = str(final_answer)
        print(f"\n🎯 Answer: {answer}")
        
        # Submit the answer
        payload = {
            "email": email,
            "secret": secret,
            "url": stage_url,
            "answer": answer
        }
        
        print(f"\nSubmitting to {submit_url}...")
        submit_response = await client.post(submit_url, json=payload)
        result = submit_response.json()
        
        print(f"\nSubmission response: {json.dumps(result, indent=2)}")
        
        if result.get('correct'):
            print(f"\n✅ SUCCESS! Next URL: {result.get('url')}")
            return result.get('url')
        else:
            print(f"\n❌ FAILED: {result.get('reason')}")
            return None

if __name__ == "__main__":
    next_url = asyncio.run(solve_stage_18())
    if next_url:
        print(f"\n🎯 Continue with: {next_url}")
