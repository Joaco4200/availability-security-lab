from fastapi import FastAPI
import httpx
import random

app = FastAPI()
failure_probability = 0.5

@app.get("/hello/")
def hello():
    if random.random() < failure_probability:
        return {"error": "Service B failed"}
    else:
        return {"message": "Hello from B!"}