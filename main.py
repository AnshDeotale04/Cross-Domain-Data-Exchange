import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import etcd3
import redis

# Config
ETCD_HOST = os.getenv("ETCD_HOST", "etcd")
ETCD_PORT = int(os.getenv("ETCD_PORT", 2379))
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Globals
etcd_client = None
redis_client = None

# Models
class RegisterPointer(BaseModel):
    entity_id: str
    owner_cluster: str
    cluster_endpoint: str

class LookupResponse(BaseModel):
    entity_id: str
    owner_cluster: str
    cluster_endpoint: str
    cache_hit: bool

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    global etcd_client, redis_client
    etcd_client = etcd3.client(host=ETCD_HOST, port=ETCD_PORT)
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    print("CRS connected to etcd and Redis")
    yield
    redis_client.close()

app = FastAPI(title="Central Registry Server", lifespan=lifespan)

# Routes
@app.get("/health")
def health():
    return {"status": "ok", "service": "crs"}

@app.post("/register")
def register_pointer(req: RegisterPointer):
    key = f"/cddx/entities/{req.entity_id}"
    value = f"{req.owner_cluster}|{req.cluster_endpoint}"
    etcd_client.put(key, value)
    redis_client.setex(f"ptr:{req.entity_id}", 300, value)
    print(f"Registered: {req.entity_id} -> {req.owner_cluster}")
    return {"registered": True, "entity_id": req.entity_id}

@app.get("/lookup/{entity_id}")
def lookup_pointer(entity_id: str) -> LookupResponse:
    # Check cache
    cached = redis_client.get(f"ptr:{entity_id}")
    if cached:
        owner, endpoint = cached.split("|")
        return LookupResponse(
            entity_id=entity_id,
            owner_cluster=owner,
            cluster_endpoint=endpoint,
            cache_hit=True
        )
    
    # Check etcd
    value, _ = etcd_client.get(f"/cddx/entities/{entity_id}")
    if not value:
        raise HTTPException(status_code=404, detail="Entity not found in registry")
    
    owner, endpoint = value.decode().split("|")
    redis_client.setex(f"ptr:{entity_id}", 300, f"{owner}|{endpoint}")
    
    return LookupResponse(
        entity_id=entity_id,
        owner_cluster=owner,
        cluster_endpoint=endpoint,
        cache_hit=False
    )