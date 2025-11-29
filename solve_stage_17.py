import httpx
import json
import asyncio
from PIL import Image
from io import BytesIO

async def solve_stage_17():
    """Stage 17: Count differing pixels between two images"""
    email = "24ds3000019@ds.study.iitm.ac.in"
    secret = "banana"
    submit_url = "https://tds-llm-analysis.s-anand.net/submit"
    stage_url = "https://tds-llm-analysis.s-anand.net/project2-diff"
    before_url = "https://tds-llm-analysis.s-anand.net/project2/before.png"
    after_url = "https://tds-llm-analysis.s-anand.net/project2/after.png"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Download both images
        print("Downloading before.png...")
        before_response = await client.get(before_url)
        before_img = Image.open(BytesIO(before_response.content)).convert('RGB')
        
        print("Downloading after.png...")
        after_response = await client.get(after_url)
        after_img = Image.open(BytesIO(after_response.content)).convert('RGB')
        
        print(f"Before image size: {before_img.size}")
        print(f"After image size: {after_img.size}")
        
        # Check if images have the same dimensions
        if before_img.size != after_img.size:
            print("❌ Images have different sizes!")
            return None
        
        # Compare pixels
        before_pixels = list(before_img.getdata())
        after_pixels = list(after_img.getdata())
        
        diff_count = 0
        for i, (before_pixel, after_pixel) in enumerate(zip(before_pixels, after_pixels)):
            if before_pixel != after_pixel:
                diff_count += 1
        
        print(f"\nTotal pixels: {len(before_pixels)}")
        print(f"Differing pixels: {diff_count}")
        
        answer = str(diff_count)
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
    next_url = asyncio.run(solve_stage_17())
    if next_url:
        print(f"\n🎯 Continue with: {next_url}")
