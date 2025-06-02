from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from http import HTTPStatus
import os
from api.services.extractDataHouseService import ExtractDataHouseService



router_house = APIRouter(prefix="/api/extract-data-house")
service = ExtractDataHouseService()

@router_house.post('', status_code=HTTPStatus.OK)
async def extract_data_house(file: Annotated[UploadFile, File()]):

    if not file.filename.endswith('.pdf'):
       raise HTTPException(
           status_code=400, detail= "Accept only pdf files"
       )
    
    save_path = os.path.join("uploads", file.filename)
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, "wb") as buffer:
        buffer.write(await file.read())
        buffer.close()

    try:
        data = service.extract_data(save_path)
        return JSONResponse(
        content={"message": "Data extracted successfully", "data": data}, 
        status_code=HTTPStatus.OK
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
