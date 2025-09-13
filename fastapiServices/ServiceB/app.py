from fastapi import FastAPI
import httpx
import random

app = FastAPI()
failure_probability = 0.5  # 30% to fail

@app.get("/hello/")
def hello():
    if random.random() < failure_probability:
        return {"error": "Service B failed"}
    return {"message": "Hello from B!"}