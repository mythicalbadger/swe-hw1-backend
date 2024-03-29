"""The main module of the application, run when the application is started."""
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.database as database
from src.swe_hw1_backend.routers import leave_requests, users

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users, i.e., login and registration.",
    },
    {
        "name": "leave_requests",
        "description": "Operations with leave requests, i.e, CRUD stuff.",
    },
]

origins = [
    "http://localhost:3000",
]


app = FastAPI(openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(leave_requests.router)


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    """Startup event handler."""
    database.init_db()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
