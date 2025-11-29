import httpx
import pandas as pd
import json
from io import StringIO
import asyncio

async def solve_stage_11():
    """Stage 11: Compute top 3 customers by total order amount"""
    email = "24ds3000019@ds.study.iitm.ac.in"
    secret = "banana"
    submit_url = "https://tds-llm-analysis.s-anand.net/submit"
    stage_url = "https://tds-llm-analysis.s-anand.net/project2-orders"
    csv_url = "https://tds-llm-analysis.s-anand.net/project2/orders.csv"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Download the CSV
        print("Downloading orders.csv...")
        response = await client.get(csv_url)
        
        # Parse CSV
        df = pd.read_csv(StringIO(response.text))
        print(f"Downloaded {len(df)} orders")
        print(df.to_string())
        
        # Group by customer_id and sum the amounts
        customer_totals = df.groupby('customer_id')['amount'].sum().reset_index()
        customer_totals.columns = ['customer_id', 'total']
        
        # Sort by total descending and take top 3
        top_3 = customer_totals.sort_values('total', ascending=False).head(3)
        
        # Convert to the required format
        answer = top_3.to_dict('records')
        print(f"\nTop 3 customers:")
        for rank, customer in enumerate(answer, 1):
            print(f"{rank}. Customer {customer['customer_id']}: ${customer['total']}")
        
        # Convert to JSON string
        answer_json = json.dumps(answer)
        print(f"\nAnswer JSON: {answer_json}")
        
        # Submit the answer
        payload = {
            "email": email,
            "secret": secret,
            "url": stage_url,
            "answer": answer_json
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
    next_url = asyncio.run(solve_stage_11())
    if next_url:
        print(f"\n🎯 Continue with: {next_url}")
