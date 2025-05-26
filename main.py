from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import yt_dlp
import requests
import os

app = FastAPI()

# Configuração do CORS (permite chamadas externas, como do frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    name: str
    email: str
    link_do_video: str
    quantidade_cortes: int
    tipo_video: str
    observacao: Optional[str] = None

def baixar_video(link: str, destino: str = "videos") -> str:
    os.makedirs(destino, exist_ok=True)

    try:
        if any(site in link for site in ["youtube.com", "youtu.be", "vimeo.com", "tiktok.com"]):
            ydl_opts = {
                'proxy': 'http://brd-customer-hl_cf51859a-zone-scraping_browser1:4o7qhh7u0lj2@brd.superproxy.io:33335',
                'outtmpl': os.path.join(destino, '%(title)s.%(ext)s'),
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'noplaylist': True,
                'quiet': False,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive'
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                file_path = ydl.prepare_filename(info)
                return file_path.replace(".webm", ".mp4").replace(".mkv", ".mp4")

        elif link.endswith((".mp4", ".mov")):
            nome_arquivo = os.path.join(destino, os.path.basename(link))
            with requests.get(link, stream=True) as r:
                r.raise_for_status()
                with open(nome_arquivo, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return nome_arquivo

        else:
            raise ValueError("Tipo de link não suportado ou vídeo não está disponível publicamente.")

    except Exception as e:
        raise RuntimeError(f"Erro ao tentar baixar o vídeo: {str(e)}")

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

    return {
        "status": "ok",
        "mensagem": "Vídeo baixado com sucesso",
        "caminho": caminho_video
    }
