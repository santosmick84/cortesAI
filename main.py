from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from pytube import YouTube
import yt_dlp
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

    # Caso o link seja de YouTube ou outra plataforma suportada
    if "youtube.com" in link or "youtu.be" in link or "vimeo.com" in link or "tiktok.com" in link:
        ydl_opts = {
            'outtmpl': os.path.join(destino, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info)
            return file_path.replace(".webm", ".mp4").replace(".mkv", ".mp4")

    # Caso seja link direto para .mp4 ou .mov
    elif link.endswith((".mp4", ".mov")):
        nome_arquivo = os.path.join(destino, os.path.basename(link))
        with requests.get(link, stream=True) as r:
            r.raise_for_status()
            with open(nome_arquivo, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return nome_arquivo

    else:
        raise ValueError("Tipo de link não suportado ou não é público.")
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
