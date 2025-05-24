from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from pytube import YouTube
import requests
import os

app = FastAPI()

class VideoRequest(BaseModel):
    name: str
    email: str
    link_do_video: str
    quantidade_cortes: int
    tipo_video: str
    observacao: Optional[str] = None

def baixar_video(link: str, destino: str = "videos") -> str:
    os.makedirs(destino, exist_ok=True)

    if "youtube.com" in link or "youtu.be" in link:
        yt = YouTube(link)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        file_path = stream.download(output_path=destino)
        return file_path

    elif link.endswith((".mp4", ".mov")):
        nome_arquivo = os.path.join(destino, os.path.basename(link))
        with requests.get(link, stream=True) as r:
            r.raise_for_status()
            with open(nome_arquivo, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return nome_arquivo

    else:
        raise ValueError("Tipo de link não suportado.")

@app.post("/process-video")
async def process_video(data: VideoRequest):
    print("✅ Dados recebidos:")
    print(data.dict())

    try:
        caminho_video = baixar_video(data.link_do_video)
        print(f"📥 Vídeo baixado com sucesso: {caminho_video}")
    except Exception as e:
        print(f"❌ Erro ao baixar vídeo: {e}")
        return {"status": "erro", "mensagem": str(e)}

    return {"status": "ok", "mensagem": "Vídeo baixado com sucesso", "caminho": caminho_video}