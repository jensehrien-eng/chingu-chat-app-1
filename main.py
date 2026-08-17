import uuid
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

class DesignRequest(BaseModel):
    text: str          
    instruction: str   

@app.get("/")
def home_check():
    return {"status": "Korean Voice Gateway is live and healthy!"}

@app.post("/generate_voice")
def generate_voice(request: DesignRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    unique_filename = f"chat_msg_{uuid.uuid4().hex}.mp3"
    
    # Connect directly to the optimized public FireRedTTS3 cluster engine
    hf_api_url = "https://hf.space"
    
    # Exact structure requested by the official Instruct platform
    payload = {
        "data": [
            request.instruction,  # Voice style instructions
            request.text,         # Speaking text characters
            "ko",                 # Korean Language tag token
            0.7,                  # Sampling temperature
            0.8,                  # top_p
            20,                   # top_k
            1.0                   # Repetition penalty
        ]
    }
    
    try:
        # Route your phone payload straight up to the cluster machines
        response = requests.post(hf_api_url, json=payload, timeout=60)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Voice cluster processing failed")
            
        # Extract the temporary audio file download url from the cluster response
        audio_url = response.json()["data"][0]["url"]
        
        # Pull down the raw binary audio and store it temporarily on Render
        audio_data = requests.get(audio_url, stream=True)
        with open(unique_filename, 'wb') as f:
            for chunk in audio_data.iter_content(chunk_size=4096):
                f.write(chunk)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy connection loss: {str(e)}")
        
    return FileResponse(unique_filename, media_type="audio/mpeg", filename=unique_filename)
