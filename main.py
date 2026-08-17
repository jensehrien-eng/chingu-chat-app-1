import os
import sys
import uuid
import shutil
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

# 1. Automate official Quick Start file structural download
if not os.path.exists("FireRedTTS3-main"):
    print("Step A: Downloading FireRedTTS3 source code folder...")
    os.system("curl -L https://github.com -o repo.zip")
    os.system("unzip -q repo.zip")
    # Move the library directory directly to root
    shutil.copytree("FireRedTTS3-main/fireredtts3", "./fireredtts3", dirs_exist_ok=True)

# 2. Automate official Model Download CLI instruction
if not os.path.exists("pretrained_models"):
    print("Step B: Fetching model weights from Hugging Face repository...")
    os.system("huggingface-cli download FireRedTeam/FireRedTTS3 --local-dir pretrained_models/")

# Add current active working directory to Python system engine path routing
sys.path.append(os.path.abspath("."))

from fireredtts3.core import FireRedTTS3Instruct

print("Step C: Booting Korean instruct voice engine on CPU...")
# Initialize the model weights exactly out of the folder target
model = FireRedTTS3Instruct("pretrained_models", use_wetext=True, use_llm_tn=False)
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
    
    # Run the official Voice Design calculation
    gen_audio, gen_audio_sr, _ = model.generate_voice_design(
        instruction=request.instruction,
        text=request.text,
        language="ko"
    )
    
    # Save internal audio vectors to file output
    import torchaudio
    torchaudio.save(unique_filename, gen_audio.cpu(), gen_audio_sr)
    
    return FileResponse(unique_filename, media_type="audio/mpeg", filename=unique_filename)

