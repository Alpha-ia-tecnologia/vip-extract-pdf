from fastapi import FastAPI
from app.controllers.extractDataCarController import router_car
from app.controllers.extractDataHouseController import router_house
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router_car)
app.include_router(router_house)



@app.get("/api")
async def read_root():
    return {"message": "Welcome to the API"}
