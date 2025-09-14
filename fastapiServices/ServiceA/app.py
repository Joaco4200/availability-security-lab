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


@app.get("/hello/replics")
async def hello():
    errors = []
    replicas_shuffled = random.sample(replicas, len(replicas))
    
    for replica in replicas_shuffled:
        logging.info(f"Trying replica {replica}")
        try:            
            async with httpx.AsyncClient(timeout=2.0) as client: #llamada http asincrona si demora mas de 2s falla.
                resp = await client.get(f"{replica}/hello/") #llamada a serviceBX
                resp_json = resp.json()
                
                if resp.status_code == 200 and "message" in resp_json:
                    logging.info(f"Réplic {replica} responded: {resp_json}")
                    return {"replic that responded": replica, "response": resp.json(), "attempted_replicas": errors}
                else:
                    logging.warning(f"Réplic {replica} responded with error: {resp_json}")
                    errors.append({replica: resp_json}) 
        finally:
            await asyncio.sleep(7)  # delay entre intentos

    print("All replicas failed")
    return {"error": "All replicas failed","attempted_replicas": errors}

@app.get("/hello/retries")
def hello_retries():
    tries= 0
    for i in range(20):
        tries +=1
        resp= httpx.get("http://service_b1:8001/hello/", timeout=2.0)
        
        if resp.status_code == 200 and "message" in resp.json():
            return {"response": resp.json(), "tries": tries}
    
    return "All retries failed"