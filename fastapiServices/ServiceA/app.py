import re
from fastapi import FastAPI, HTTPException, HTTPBasicCredentials, Depends, Optional, Dict, HTTPBasic, BaseModel, status
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

MAX_RETRIES = 3

# Tactica de seguridad 1: Autenticar actores
# =============================================================================

USER_DATABASE = {
    "admin": {
        "password": "admin123",
        "role": "admin"
    },
    "user1": {
        "password": "password123", 
        "role": "user"
    },
    "student": {
        "password": "student123",
        "role": "student"
    }
}

security_basic = HTTPBasic()

class UserCredentials(BaseModel):
    username: str
    password: str

def verify_user(username: str, password: str) -> Optional[Dict[str, str]]:
    user = USER_DATABASE.get(username)
    if user and user["password"] == password:
        logging.info(f"Usuario {username} autenticado correctamente")
        return {
            "user_id": username,
            "role": user["role"]
        }
    logging.warning(f"Intento de autenticación fallido para usuario {username}")
    return None

async def authenticate_actor(
        credentials: HTTPBasicCredentials = Depends(security_basic)
    ) -> Dict[str, str]:
    username = credentials.username
    password = credentials.password
    
    logging.info(f"Intento de autenticación para usuario: {username}")
    
    # Verificar credenciales
    user_info = verify_user(username, password)
    if user_info:
        return {
            "user_id": user_info["user_id"],
            "role": user_info["role"],
            "auth_method": "basic_auth"
        }
    else:
        logging.warning(f"Credenciales inválidas para usuario: {username}")
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"Authorization": "Basic"}
        )

@app.get("/api/auth/user")
async def user_authentication(user_info: Dict[str, str] = Depends(authenticate_actor)):

    return {
        "message": "Autenticación exitosa",
        "user_info": user_info,
        "status": "authenticated"
    }

@app.post("/api/auth/verify_credentials")
async def verify_credentials(credentials: UserCredentials):

    user_info = verify_user(credentials.username, credentials.password)
    if user_info:
        return {
            "message": "Credenciales válidas",
            "user_info": {
                "user_id": user_info["user_id"],
                "role": user_info["role"],
                "auth_method": "credential_verification"
            },
            "status": "valid"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

#Tactica de disponibilidad: replicacion
# =============================================================================
@app.get("/api/replicas")
async def hello():
    errors = []
    # replicas_shuffled = random.sample(replicas, len(replicas))
    
    for replica in replicas:
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
            await asyncio.sleep(1)  # delay entre intentos

    return {"error": "All replicas failed","attempted_replicas": errors}

#Tactica de disponibilidad: re-intentos
# =============================================================================
@app.get("/api/retries")
async def hello_retries():
    tries = 0
    for i in range(MAX_RETRIES):
        tries +=1
        resp= httpx.get("http://service_b1:8001/hello/", timeout=2.0)
        
        if resp.status_code == 200 and "message" in resp.json():
            return {"response": resp.json(), "tries": tries}

    return {"error": "All retries failed"}

