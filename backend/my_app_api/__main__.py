import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from my_app_api.routes import auth
from my_app_api.routes import locations
from my_app_api.routes import clusters
from my_app_api.routes import wells
from my_app_api.routes import well_states
from my_app_api.routes import reports


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(locations.router)
app.include_router(clusters.router)
app.include_router(wells.router)
app.include_router(well_states.router)
app.include_router(reports.router)


@app.get("/")
def read_root():
    return {"message": "API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
