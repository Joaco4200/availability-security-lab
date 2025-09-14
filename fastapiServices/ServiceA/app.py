from fastapi import FastAPI, HTTPException
import httpx
import asyncio
import random

app= FastAPI()

replicas = [
    "http://service_b1:8000",
    "http://service_b2:8000",
    "http://service_b3:8000",
]

@app.get("/hello/")
async def hello():
    errors = []
    for _ in range(len(replicas)):
        replica = random.choice(replicas)
        try:            
            async with httpx.AsyncClient(timeout=2.0) as client: #llamada http asincrona si demora mas de 2s falla.
                resp = await client.get(f"{replica}/hello")

                if resp.status_code == 200 and "message" in resp.json():
                    print(f"Replica {replica} responded successfully")
                    return {"replic that responded": replica, "response": resp.json(), "attempted_replicas": errors}
                else:
                     print(f"Replica {replica} responded with unexpected data: {resp_json}")
                     errors.append({replica: resp_json})

        except Exception as e:
            print(f"Error with replica {replica}: {e}")
            errors.append({replica: str(e)})
            continue
    return {"error": "All replicas failed","attempted_replicas": errors}
