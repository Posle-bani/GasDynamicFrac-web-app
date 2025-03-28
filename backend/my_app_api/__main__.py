import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from my_app_api.routes import auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
