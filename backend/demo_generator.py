"""
Demo script to generate traces for AgentScope
"""
import time
import random
import uuid
from datetime import datetime, timezone
import requests

API_URL = "http://localhost:8000/api/v1/traces"
PROJECT_ID = "default-project"

def generate_mock_trace():
    trace_id = str(uuid.uuid4())
    names = ["CustomerSupportAI", "TranslationBot", "DataAnalyzer", "RiskAssessor", "AutoCoder"]
    name = random.choice(names)
    
    start_time = datetime.now(timezone.utc)
    status = "success" if random.random() > 0.1 else "error"
    error_msg = "Rate limit exceeded" if status == "error" else None
    
    # Generate 2-5 spans
    spans = []
    num_spans = random.randint(2, 5)
    total_cost = 0.0
    total_tokens = 0
    
    for i in range(num_spans):
        span_start = datetime.now(timezone.utc)
        time.sleep(random.uniform(0.1, 0.5))
        span_end = datetime.now(timezone.utc)
        
        duration = int((span_end - span_start).total_seconds() * 1000)
        
        span_types = ["llm", "tool", "function"]
        s_type = random.choice(span_types)
        
        cost = 0.0
        tokens = 0
        model = None
        
        if s_type == "llm":
            models = ["gpt-4o", "gpt-4o-mini", "claude-3-sonnet", "gpt-3.5-turbo"]
            model = random.choice(models)
            tokens = random.randint(100, 2000)
            cost = (tokens / 1000) * 0.01
            total_cost += cost
            total_tokens += tokens
            
        spans.append({
            "id": str(uuid.uuid4()),
            "name": f"Step {i+1}",
            "span_type": s_type,
            "start_time": span_start.isoformat(),
            "end_time": span_end.isoformat(),
            "duration_ms": duration,
            "model": model,
            "input_tokens": tokens if s_type == "llm" else None,
            "output_tokens": tokens // 2 if s_type == "llm" else None,
            "cost_usd": cost if s_type == "llm" else None,
            "status": "success",
            "input_data": {"query": "hello"},
            "output_data": {"response": "hi"}
        })

    end_time = datetime.now(timezone.utc)
    duration = int((end_time - start_time).total_seconds() * 1000)

    trace_data = {
        "id": trace_id,
        "project_id": PROJECT_ID,
        "name": name,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_ms": duration,
        "status": status,
        "error_message": error_msg,
        "extra_metadata": {},
        "spans": spans
    }
    
    try:
        response = requests.post(
            API_URL, 
            json=trace_data,
            headers={"X-API-KEY": "sk_demo_key_12345"}
        )
        if response.status_code == 200:
            print(f"Sent trace: {name} ({status})")
        else:
            print(f"Failed to send trace: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Generating mock data... Press Ctrl+C to stop.")
    while True:
        generate_mock_trace()
        time.sleep(random.uniform(2, 8))
