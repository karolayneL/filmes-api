import os
from typing import Optional, List
from uuid import UUID
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
import httpx
import uvicorn
from datetime import date

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
TABLE = os.getenv("TABLE_MOVIES", "movies")
POSTGREST_URL = f"{SUPABASE_URL}/rest/v1"

if not SUPABASE_URL or not ANON_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_ANON_KEY not found.")

app = FastAPI(title="Movies API")

class MovieCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str
    release_year: int = Field(ge=1888, le=date.today().year)
    duration: int = Field(ge=1, description="Duração em minutos")
    genre: str = Field(max_length=100)
    director: str = Field(max_length=100)
    rating: float = Field(ge=0, le=10)
    user_id: UUID

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    release_year: Optional[int] = Field(default=None, ge=1888, le=date.today().year)
    duration: Optional[int] = Field(default=None, ge=1)
    genre: Optional[str] = Field(default=None, max_length=100)
    director: Optional[str] = Field(default=None, max_length=100)
    rating: Optional[float] = Field(default=None, ge=0, le=10)

class MovieOut(BaseModel):
    id: UUID
    title: str
    description: str
    release_year: int
    duration: int
    genre: str
    director: str
    rating: float
    user_id: UUID
    created_at: str
    updated_at: str

async def get_user_token(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Missing or invalid Authorization header"
        )
    return authorization

def postgrest_headers(user_authorization: str):
    return {
        "apikey": ANON_KEY,
        "Authorization": user_authorization,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Prefer": "return=representation",
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/movies", response_model=List[MovieOut])
async def list_movies(
    auth=Depends(get_user_token), 
    limit: int = 50, 
    offset: int = 0, 
    genre: Optional[str] = None,
    director: Optional[str] = None,
    min_rating: Optional[float] = None
):
    params = {
        "select": "*", 
        "limit": str(min(limit, 100)), 
        "offset": str(max(offset, 0)), 
        "order": "created_at.desc"
    }
    
    if genre:
        params["genre"] = f"ilike.*{genre}*"
    if director:
        params["director"] = f"ilike.*{director}*"
    if min_rating is not None:
        params["rating"] = f"gte.{min_rating}"
    
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{POSTGREST_URL}/{TABLE}", headers=postgrest_headers(auth), params=params)
    
    if r.status_code >= 400:
        raise HTTPException(r.status_code, r.text)
    return r.json()

@app.get("/movies/{movie_id}", response_model=List[MovieOut])
async def get_movie(movie_id: UUID, auth=Depends(get_user_token)):
    params = {"select": "*", "id": f"eq.{movie_id}"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{POSTGREST_URL}/{TABLE}", headers=postgrest_headers(auth), params=params)
    
    if r.status_code >= 400:
        raise HTTPException(r.status_code, r.text)
    
    result = r.json()
    if not result:
        raise HTTPException(status_code=404, detail="Movie not found")
    return result

@app.post("/movies", response_model=List[MovieOut], status_code=201)
async def create_movie(payload: MovieCreate, auth=Depends(get_user_token)):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{POSTGREST_URL}/{TABLE}",
            headers=postgrest_headers(auth),
            json=payload.model_dump(mode="json")
        )
    
    if r.status_code >= 400:
        raise HTTPException(r.status_code, r.text)
    return r.json()

@app.put("/movies/{movie_id}", response_model=List[MovieOut])
async def update_movie(movie_id: UUID, payload: MovieUpdate, auth=Depends(get_user_token)):
    data = {k: v for k, v in payload.model_dump(mode="json").items() if v is not None}
    
    if not data:
        raise HTTPException(400, "No fields to update")
    
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.patch(
            f"{POSTGREST_URL}/{TABLE}",
            headers=postgrest_headers(auth),
            params={"id": f"eq.{movie_id}"},
            json=data,
        )
    
    if r.status_code >= 400:
        raise HTTPException(r.status_code, r.text)
    
    result = r.json()
    if not result:
        raise HTTPException(status_code=404, detail="Movie not found")
    return result

@app.delete("/movies/{movie_id}", status_code=204)
async def delete_movie(movie_id: UUID, auth=Depends(get_user_token)):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.delete(
            f"{POSTGREST_URL}/{TABLE}",
            headers=postgrest_headers(auth),
            params={"id": f"eq.{movie_id}"},
        )
    
    if r.status_code >= 400:
        raise HTTPException(r.status_code, r.text)
    
    if r.status_code == 204:
        return {}
    else:
        # Se não retornou 204, verifica se o filme existia
        check_response = await get_movie(movie_id, auth)
        if not check_response:
            raise HTTPException(status_code=404, detail="Movie not found")
        return {}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
