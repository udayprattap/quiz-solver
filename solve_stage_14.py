import httpx
import json
import asyncio

async def solve_stage_14():
    """Stage 14: Find optimal shards and replicas configuration"""
    email = "24ds3000019@ds.study.iitm.ac.in"
    secret = "banana"
    submit_url = "https://tds-llm-analysis.s-anand.net/submit"
    stage_url = "https://tds-llm-analysis.s-anand.net/project2-shards"
    json_url = "https://tds-llm-analysis.s-anand.net/project2/shards.json"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Download the constraints
        print("Downloading shards.json...")
        response = await client.get(json_url)
        constraints = response.json()
        
        print(f"Constraints: {json.dumps(constraints, indent=2)}")
        
        dataset = constraints['dataset']
        max_docs_per_shard = constraints['max_docs_per_shard']
        max_shards = constraints['max_shards']
        min_replicas = constraints['min_replicas']
        max_replicas = constraints['max_replicas']
        memory_per_shard = constraints['memory_per_shard']
        memory_budget = constraints['memory_budget']
        
        print(f"\nFinding valid configuration:")
        print(f"- Need to distribute {dataset} docs")
        print(f"- Each shard can hold max {max_docs_per_shard} docs")
        print(f"- Max {max_shards} shards allowed")
        print(f"- Replicas must be {min_replicas}-{max_replicas}")
        print(f"- Each shard uses {memory_per_shard}GB memory")
        print(f"- Total memory budget: {memory_budget}GB")
        
        # Find valid configurations
        valid_configs = []
        
        for shards in range(1, max_shards + 1):
            # Check if shards can hold all docs
            if shards * max_docs_per_shard < dataset:
                continue
            
            for replicas in range(min_replicas, max_replicas + 1):
                # Check memory constraint
                total_memory = shards * replicas * memory_per_shard
                if total_memory <= memory_budget:
                    valid_configs.append({
                        'shards': shards,
                        'replicas': replicas,
                        'docs_per_shard': dataset / shards,
                        'total_memory': total_memory
                    })
                    print(f"\n✓ Valid: shards={shards}, replicas={replicas}")
                    print(f"  - Docs per shard: {dataset/shards:.1f}")
                    print(f"  - Total memory: {total_memory}GB")
        
        if not valid_configs:
            print("\n❌ No valid configuration found!")
            return None
        
        # Pick the first valid configuration (or optimize based on criteria)
        best_config = valid_configs[0]
        
        answer = {
            "shards": best_config['shards'],
            "replicas": best_config['replicas']
        }
        
        answer_json = json.dumps(answer)
        print(f"\n🎯 Selected answer: {answer_json}")
        
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
    next_url = asyncio.run(solve_stage_14())
    if next_url:
        print(f"\n🎯 Continue with: {next_url}")
