from fastapi import FastAPI, HTTPException
import httpx
import asyncio
import random
import logging

app= FastAPI()
logging.basicConfig(level=logging.INFO)

replicas = [
    "http://service_b1:8001",
    "http://service_b2:8001",
    "http://service_b3:8001",
]


@app.get("/hello/")
async def hello():
    errors = []
    for _ in range(len(replicas)):
        replica = random.choice(replicas)
        logging.info(f"Trying replica {replica}")
        try:            
            async with httpx.AsyncClient(timeout=2.0) as client: #llamada http asincrona si demora mas de 2s falla.
                resp = await client.get(f"{replica}/hello/")
                resp_json = resp.json()
                
                if resp.status_code == 200:
                    logging.info(f"Réplica {replica} respondió correctamente: {resp_json}")
                    return {"replic that responded": replica, "response": resp.json(), "attempted_replicas": errors}
                else:
                    logging.warning(f"Réplica {replica} respondió incorrectamente: {resp_json}")
                    errors.append({replica: resp_json})

        except Exception as e:
            errors.append({replica: str(e)})
            continue

    print("All replicas failed")
    return {"error": "All replicas failed","attempted_replicas": errors}
