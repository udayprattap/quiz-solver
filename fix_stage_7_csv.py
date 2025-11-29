import httpx
import pandas as pd
import json
import asyncio
from io import StringIO

async def solve_stage_7_csv():
    """Stage 7: CSV normalization - trying different formats"""
    email = "24ds3000019@ds.study.iitm.ac.in"
    secret = "banana"
    submit_url = "https://tds-llm-analysis.s-anand.net/submit"
    stage_url = "https://tds-llm-analysis.s-anand.net/project2-csv"
    csv_url = "https://tds-llm-analysis.s-anand.net/project2/messy.csv"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Download CSV
        response = await client.get(csv_url)
        csv_content = response.text
        print("Original CSV:")
        print(csv_content)
        print()
        
        # Parse CSV
        df = pd.read_csv(StringIO(csv_content))
        
        # Normalize column names to snake_case
        df.columns = [col.lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        
        # Normalize dates to ISO-8601
        df['joined'] = pd.to_datetime(df['joined'], format='mixed').dt.strftime('%Y-%m-%d')
        
        # Ensure value is integer
        df['value'] = df['value'].astype(int)
        
        # Sort by id ascending
        df = df.sort_values('id')
        
        print("Processed DataFrame:")
        print(df)
        print()
        
        # Try different JSON formats
        formats = [
            ("records with spaces", df.to_json(orient='records')),
            ("records compact", df.to_json(orient='records', indent=None)),
            ("records no separators", json.dumps(df.to_dict('records'), separators=(',', ':'))),
            ("records with space after colon", json.dumps(df.to_dict('records'), separators=(',', ': '))),
            ("records no ensure_ascii", json.dumps(df.to_dict('records'), ensure_ascii=False)),
        ]
        
        for format_name, answer in formats:
            print(f"\nTrying format: {format_name}")
            print(f"Answer preview: {answer[:100]}...")
            
            payload = {
                "email": email,
                "secret": secret,
                "url": stage_url,
                "answer": answer
            }
            
            response = await client.post(submit_url, json=payload)
            result = response.json()
            
            if result.get('correct'):
                print(f"✅ SUCCESS with format: {format_name}")
                print(f"Answer: {answer}")
                print(f"Response: {json.dumps(result, indent=2)}")
                return answer
            else:
                print(f"❌ Failed: {result.get('reason')}")
        
        return None

if __name__ == "__main__":
    asyncio.run(solve_stage_7_csv())
