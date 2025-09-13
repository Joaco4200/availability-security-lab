from fastapi import FastAPI, HTTPException
import httpx
import asyncio
import requests

app= FastAPI()

replicas = [
    "http://service_b1:8000",
    "http://service_b2:8000",
    "http://service_b3:8000",
]

@app.get("/hello")
async def hello():
    for _ in range(len(replicas)):
        replica = random.choice(replicas)
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{replica}/hello")
                if resp.status_code == 200 and "message" in resp.json():
                    return {"replica": replica, "response": resp.json()}
        except Exception:
            continue
    return {"error": "All replicas failed"}
