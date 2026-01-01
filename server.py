import uvicorn
import os
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.orchestrator import Orchestrator
from src.models.schemas import UserProvidedImage
from src.services.cloudinary_service import CloudinaryService

app = FastAPI(title="Invincible PPT Agent")

class PPTRequest(BaseModel):
    prompt: str
    images: list[UserProvidedImage] = [] 

@app.post("/generate-ppt")
async def generate_ppt(request: PPTRequest):
    """
    Triggers the AI Agent to build a presentation.
    Uploads result to Cloudinary and returns the URL.
    """
    file_path = ""
    try:
        orchestrator = Orchestrator()
        
        # 1. RUN WORKFLOW (Generates local .pptx in temp/)
        file_path = await orchestrator.run_workflow(request.prompt, request.images)
        
        # 2. UPLOAD TO CLOUDINARY
        unique_id = f"ppt_{uuid.uuid4().hex[:8]}"
        cloudinary_url = CloudinaryService.upload_ppt(file_path, unique_id)
        
        # 3. FINAL CLEANUP
        # Orchestrator cleans images, but we must clean the final PPT here
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✨ Final PPT cleanup: Deleted {file_path}")
            
        # 4. RETURN URL
        return {
            "status": "success",
            "message": "Presentation generated successfully",
            "ppt_url": cloudinary_url
        }
        
    except Exception as e:
        # Emergency cleanup
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)