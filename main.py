from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class VideoRequest(BaseModel):
    name: str
    email: str
    link_do_video: str
    quantidade_cortes: int
    tipo_video: str
    observacao: Optional[str] = None

@app.post("/process-video")
async def process_video(data: VideoRequest):
    print("✅ Dados recebidos:")
    print(data.dict())
    return {"status": "ok", "mensagem": "Vídeo recebido para processamento"}