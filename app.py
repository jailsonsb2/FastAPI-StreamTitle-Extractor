from fastapi import FastAPI, HTTPException, Request
from typing import Optional, Tuple
import urllib.request
from fastapi.middleware.cors import CORSMiddleware
import requests
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi.responses import HTMLResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_album_art(artist: str, song: str) -> Optional[str]:
    """Busca a capa do álbum na iTunes API."""
    try:
        response = requests.get(
            f"https://itunes.apple.com/search?term={artist}+{song}&media=music&limit=1"
        )
        response.raise_for_status()
        data = response.json()
        if data["resultCount"] > 0:
            return data["results"][0]["artworkUrl100"].replace("100x100bb", "512x512bb")
        else:
            return None  # Retorna None se não encontrar a capa
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar capa do álbum: {e}")
        return None

def get_mp3_stream_title(streaming_url: str, interval: int) -> Optional[str]:
    """Busca o título da música em um stream MP3."""
    try:
        needle = b'StreamTitle='
        ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36'
        headers = {
            'Icy-MetaData': '1',
            'User-Agent': ua
        }
        req = urllib.request.Request(streaming_url, headers=headers)
        response = urllib.request.urlopen(req)
        
        meta_data_interval = None
        for key, value in response.headers.items():
            if key.lower() == 'icy-metaint':
                meta_data_interval = int(value)
                break

        if meta_data_interval is None:
            return None

        offset = 0
        while True:
            response.read(meta_data_interval)
            buffer = response.read(interval)
            title_index = buffer.find(needle)
            if title_index != -1:
                title = buffer[title_index + len(needle):].split(b';')[0].decode('utf-8')
                return title
            offset += meta_data_interval + interval
    except Exception as e:
        print(f"Erro ao buscar título da música: {e}")
        return None


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>API de Streaming de Música</title>
        </head>
        <body>
            <h1>Bem-vindo à API de Streaming de Música!</h1>
            <p>Use o endpoint /get_stream_title/ para obter informações da música a partir de uma URL de stream.</p>
        </body>
    </html>
    """
    
@app.get("/get_stream_title/")
@Limiter.limit("7/minute")  # Permite 5 requisições por minuto por IP
async def get_stream_title(url: str, interval: Optional[int] = 19200):
    title = get_mp3_stream_title(url, interval)
    if title:
        artist, song = extract_artist_and_song(title)
        art_url = get_album_art(artist, song)  
        return {"artist": artist, "song": song, "art": art_url} 
    else:
        raise HTTPException(status_code=404, detail="Falha ao recuperar o título do stream")

    
# Página de Erro 404 Personalizada
@app.exception_handler(404)
async def custom_404_handler(request: urllib.request.Request, exc: HTTPException):
    return HTMLResponse(
        content="""
        <html>
            <head>
                <title>404 Não Encontrado</title>
            </head>
            <body>
                <h1>Ops! Esta página não existe.</h1>
                <p>O recurso que você está procurando não foi encontrado.</p>
            </body>
        </html>
        """,
        status_code=404
    )

def extract_artist_and_song(title: str) -> Tuple[str, str]:
    """Extrai o artista e a música do título."""
    title = title.strip("'")
    
    if '-' in title:
        artist, song = title.split('-', 1)
        return artist.strip(), song.strip()
    else:
        return '', title.strip()
