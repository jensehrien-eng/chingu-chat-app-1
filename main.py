import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fireredtts3.models import FireRedTTS3

print("Booting instruct voice engine on CPU...")
# This tells the server to load the description-capable variant
model = FireRedTTS3.from_pretrained("FireRedTeam/FireRedTTS3", variant="fireredtts3_instruct")
print("Instruct engine ready!")

app = FastAPI()

class DesignRequest(BaseModel):
    text: str          
    instruction: str   

@app.get("/")
def home_check():
    return {"status": "Korean Instruct Server is awake!"}

@app.post("/generate_voice")
def generate_voice(request: DesignRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text string cannot be empty")
        
    unique_filename = f"chat_msg_{uuid.uuid4().hex}.mp3"
    
    # This runs the voice design algorithm using your description text
    model.design_voice(
        text=request.text,
        instruction=request.instruction,
        output_path=unique_filename,
        language="ko" 
    )
    
    return FileResponse(unique_filename, media_type="audio/mpeg", filename=unique_filename)
