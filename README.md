# Pasos Previos

Antes de poder levantar la aplicación, hay que tener instalado:

- **Docker**
- **Docker Compose**
  
## Ubicación para Ejecutar el Comando

Hay que ingresar a la carpeta `fastapiServices` y ejecutar el siguiente comando:
```bash
docker-compose up
```


# Casos de Uso para Testing - FastAPI Services

## 1. TÁCTICAS DE SEGURIDAD

### 1.1 Autenticación de Actores (HTTP Basic Auth)

#### Endpoint: `GET /api/auth/user`

**TC-AUTH-001**: Usuario admin válido
```bash
curl -u admin:admin123 http://localhost:8000/api/auth/user
```
**Resultado Esperado (200):**
```json
{
  "message": "Autenticación exitosa",
  "user_info": {
    "user_id": "admin",
    "role": "admin",
    "auth_method": "basic_auth"
  },
  "status": "authenticated"
}
```

**TC-AUTH-002**: Usuario inexistente
```bash
curl -u noexiste:password http://localhost:8000/api/auth/user
```
**Resultado Esperado (401):**
```json
{
  "detail": "Credenciales inválidas"
}
```

**TC-AUTH-003**: Contraseña incorrecta
```bash
curl -u admin:wrongpass http://localhost:8000/api/auth/user
```
**Resultado Esperado (401):**
```json
{
  "detail": "Credenciales inválidas"
}
```

**TC-AUTH-006**: Sin credenciales
```bash
curl http://localhost:8000/api/auth/user
```
**Resultado Esperado (401):**
```json
{
  "detail": "Not authenticated"
}
```

#### Endpoint: `POST /api/auth/verify_credentials`

**TC-VERIFY-001**: Credenciales user1 válidas
```bash
curl -X POST http://localhost:8000/api/auth/verify_credentials \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'
```
**Resultado Esperado (200):**
```json
{
  "message": "Credenciales válidas",
  "user_info": {
    "user_id": "user1",
    "role": "user",
    "auth_method": "credential_verification"
  },
  "status": "valid"
}
```

**TC-VERIFY-002**: Usuario inexistente
```bash
curl -X POST http://localhost:8000/api/auth/verify_credentials \
  -H "Content-Type: application/json" \
  -d '{"username": "fake", "password": "test"}'
```
**Resultado Esperado (401):**
```json
{
  "detail": "Credenciales inválidas"
}
```

**TC-VERIFY-003**: Campo username faltante
```bash
curl -X POST http://localhost:8000/api/auth/verify_credentials \
  -H "Content-Type: application/json" \
  -d '{"password": "admin123"}'
```
**Resultado Esperado (422):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "username"],
      "msg": "Field required",
      "input": {"password": "admin123"}
    }
  ]
}
```

### 1.2 Validación de Entrada

#### Endpoint: `POST /api/validate/message`

**TC-VAL-001**: Mensaje válido corto
```bash
curl -u admin:admin123 -X POST http://localhost:8000/api/validate/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola", "priority": 1}'
```
**Resultado Esperado (200):**
```json
{
  "status": "success",
  "message": "Mensaje válido",
  "validated_data": {
    "message": "Hola",
    "priority": 1,
    "message_length": 4
  },
  "user_info": {
    "user_id": "admin",
    "role": "admin",
    "auth_method": "basic_auth"
  }
}
```
**TC-VAL-003**: Mensaje con prioridad máxima
```bash
curl -u admin:admin123 -X POST http://localhost:8000/api/validate/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Urgente", "priority": 3}'
```
**Resultado Esperado (200):**
```json
{
  "status": "success",
  "message": "Mensaje válido",
  "validated_data": {
    "message": "Urgente",
    "priority": 3,
    "message_length": 7
  },
  "user_info": {
    "user_id": "admin",
    "role": "admin",
    "auth_method": "basic_auth"
  }
}
```

**TC-VAL-004**: Mensaje vacío
```bash
curl -u admin:admin123 -X POST http://localhost:8000/api/validate/message \
  -H "Content-Type: application/json" \
  -d '{"message": "", "priority": 1}'
```
**Resultado Esperado (400):**
```json
{
  "detail": "Error de validación: El mensaje no puede estar vacío"
}
```

**TC-VAL-005**: Mensaje con caracteres prohibidos (<)
```bash
curl -u admin:admin123 -X POST http://localhost:8000/api/validate/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola <script>", "priority": 1}'
```
**Resultado Esperado (400):**
```json
{
  "detail": "Error de validación: El mensaje no puede contener < o >"
}
```

**TC-VAL-006**: Mensaje demasiado largo
```bash
curl -u admin:admin123 -X POST http://localhost:8000/api/validate/message \
  -H "Content-Type: application/json" \
  -d '{"message": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "priority": 1}'
```
**Resultado Esperado (422):**
```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "message"],
      "msg": "String should have at most 100 characters",
      "input": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
      "ctx": {"max_length": 100}
    }
  ]
}
```

**TC-VAL-007**: Prioridad inválida (0)
```bash
curl -u admin:admin123 -X POST http://localhost:8000/api/validate/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Test", "priority": 0}'
```
**Resultado Esperado (422):**
```json
{
  "detail": [
    {
      "type": "greater_than_equal",
      "loc": ["body", "priority"],
      "msg": "Input should be greater than or equal to 1",
      "input": 0,
      "ctx": {"ge": 1}
    }
  ]
}
```

**TC-VAL-008**: Sin autenticación
```bash
curl -X POST http://localhost:8000/api/validate/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Test", "priority": 1}'
```
**Resultado Esperado (401):**
```json
{
  "detail": "Not authenticated"
}
```

#### Endpoint: `GET /api/validate/limit/{limit}`

**TC-LIM-001**: Límite máximo válido
```bash
curl -u admin:admin123 http://localhost:8000/api/validate/limit/20
```
**Resultado Esperado (200):**
```json
{
  "status": "success",
  "message": "Límite válido",
  "validated_data": {
    "limit": 20,
    "is_valid": true
  },
  "user_info": {
    "user_id": "admin",
    "role": "admin",
    "auth_method": "basic_auth"
  }
}
```

**TC-LIM-004**: Límite inválido (0)
```bash
curl -u admin:admin123 http://localhost:8000/api/validate/limit/0
```
**Resultado Esperado (400):**
```json
{
  "detail": "Error de validación: El límite debe estar entre 1 y 20"
}
```

**TC-LIM-006**: Límite negativo
```bash
curl -u admin:admin123 http://localhost:8000/api/validate/limit/-1
```
**Resultado Esperado (400):**
```json
{
  "detail": "Error de validación: El límite debe estar entre 1 y 20"
}
```

**TC-LIM-007**: Límite no numérico
```bash
curl -u admin:admin123 http://localhost:8000/api/validate/limit/abc
```
**Resultado Esperado (422):**
```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["path", "limit"],
      "msg": "Input should be a valid integer",
      "input": "abc"
    }
  ]
}
```

---

## 2. TÁCTICAS DE DISPONIBILIDAD

### 2.1 Replicación

#### Endpoint: `GET /api/replicas`

**TC-REP-001**: Primera réplica disponible (service_b1 UP, otros DOWN)
```bash
curl http://localhost:8000/api/replicas
```
**Resultado Esperado (200):**
```json
{
  "replic that responded": "http://service_b1:8001",
  "response": {
    "message": "Hello from B!"
  },
  "attempted_replicas": []
}
```

### 2.2 Re-intentos

#### Endpoint: `GET /api/retries`

**TC-RET-001**: Pruebas de cantidad de retries por replica
```bash
curl http://localhost:8000/api/retries
```
**Resultado Esperado (200) - Si service_b1 responde exitosamente:**
```json
{
  "response": {
    "message": "Hello from B!"
  },
  "tries": 1
}
```

