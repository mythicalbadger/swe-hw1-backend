"""The main module of the application, run when the application is started."""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.database as database
from src.routers import leave_requests, users

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
database.init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(leave_requests.router)


@app.get("/")
async def root() -> dict:
    """
    Return a simple JSON message. Default route.

    :return: A simple JSON message.
    """
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
