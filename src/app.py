from fastapi import FastAPI
from api.controllers.extractDataCarController import router_car
from api.controllers.extractDataHouseController import router_house


app = FastAPI()
app.include_router(router_car)
app.include_router(router_house)

@app.get("/api")
async def read_root():
    return {"message": "Welcome to the API"}