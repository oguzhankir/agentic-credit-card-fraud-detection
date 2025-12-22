
import asyncio
import json
from backend.agents.coordinator_agent import CoordinatorAgent

async def test_nuclear_risk():
    coordinator = CoordinatorAgent()
    
    # Extreme Outlier: $500,000 for Coffee at 5000km distance
    transaction = {
        "amount": 500000.0,
        "merchant": "Local Coffee",
        "category": "food_dining",
        "time": "2025-12-21T22:41",
        "location": {
            "lat": 40.7128,
            "long": -74.006,
            "distance_from_home": 5000.0,
            "state": "NY"
        },
        "customer_id": "cust_123"
    }
    
    customer_history = {
        "avg_amount": 100.0,
        "std_amount": 20.0,
        "usual_hours": [9, 10, 11, 12, 18, 19],
        "transaction_count": 50
    }
    
    print("Running Nuclear Risk Test: $500k Coffee at 5000km...")
    result = await coordinator.analyze_async(transaction, customer_history)
    
    print("\nFINAL DECISION:")
    print(json.dumps(result.get('output', {}), indent=2))
    
    # Check for nuclear saturation in the steps
    for step in result.get('steps', []):
        if step['type'] == 'OBSERVATION' and 'nuclear_saturation' in step['content']:
            print("\n✅ Nuclear Saturation Detected in Risk Scorer!")
            break

if __name__ == "__main__":
    asyncio.run(test_nuclear_risk())
