from fastapi import APIRouter, File, UploadFile, Depends
from ...services.ocr_service import process_image

router = APIRouter()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Process the uploaded image for OCR
    result = await process_image(file)
    return {"result": result}
