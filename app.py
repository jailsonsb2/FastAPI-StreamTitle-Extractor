from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import urllib.request
from typing import Optional, Tuple, Dict
import asyncio
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "radio_data"
SONG_HISTORY_LIMIT = 5

# Dicionário para armazenar informações sobre as rádios (carregadas dos arquivos)
radio_data: Dict[str, Dict] = {}
radio_data_lock = asyncio.Lock() 


# Função para obter a capa do álbum
def get_album_art(artist: str, song: str) -> Optional[str]:
    try:
        response = requests.get(
            f"https://itunes.apple.com/search?term={artist}+{song}&media=music&limit=1"
        )
        response.raise_for_status()
        data = response.json()
        if data["resultCount"] > 0:
            return data["results"][0]["artworkUrl100"].replace("100x100bb", "512x512bb")
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar capa do álbum: {e}")
        return None

# Função para obter o título da transmissão de MP3
def get_mp3_stream_title(streaming_url: str, interval: int) -> Optional[str]:
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

# Função para extrair artista e música do título
def extract_artist_and_song(title: str) -> Tuple[str, str]:
    # Remove as aspas simples extras
    title = title.strip("'")
    
    if '-' in title:
        artist, song = title.split('-', 1)
        return artist.strip(), song.strip()
    else:
        return '', title.strip()
    
async def monitor_radio(radio_url: str, background_tasks: BackgroundTasks):
    global radio_data

    async with radio_data_lock:
        if radio_url not in radio_data:
            radio_data[radio_url] = {
                "song_history": [],
                "current_song": {"artist": "", "song": ""},
                "monitoring_started": False,
            }
    
    radio = radio_data[radio_url]  # Referência direta ao dicionário da rádio
    radio["monitoring_started"] = True

    while True:
        title = get_mp3_stream_title(radio_url, 19200)
        if title:
            artist, song = extract_artist_and_song(title)
            async with radio_data_lock:
                if artist != radio["current_song"]["artist"] or song != radio["current_song"]["song"]:
                    if radio["current_song"]["artist"] and radio["current_song"]["song"]:
                        radio["song_history"].insert(0, radio["current_song"])
                        radio["song_history"] = radio["song_history"][:SONG_HISTORY_LIMIT]
                    radio["current_song"] = {"artist": artist, "song": song}
        await asyncio.sleep(10)


# Endpoint raiz
@app.get("/")
async def root():
    return {
        "message": "Welcome",
        "now_playing and cover art": "Use /get_stream_title/?url=https://example.com/stream",
        "now_playing and history": "Use /radio_info/?radio_url=https://example.com/stream",
        "contact": "contato@jailson.es"       
    }

# Endpoint para obter o título da transmissão e a capa do álbum
@app.get("/get_stream_title/")
async def get_stream_title(url: str, interval: Optional[int] = 19200):
    title = get_mp3_stream_title(url, interval)
    if title:
        artist, song = extract_artist_and_song(title)
        art_url = get_album_art(artist, song) 
        return {"artist": artist, "song": song, "art": art_url} 
    else:
        return {"error": "Failed to retrieve stream title"}

# Endpoint para obter o título da transmissão e a capa do álbum
@app.get("/metadata/")
async def get_stream_title(url: str, interval: Optional[int] = 19200):
    title = get_mp3_stream_title(url, interval)

    if title:
        artist, song = extract_artist_and_song(title)
        art_url = get_album_art(artist, song)

        # Nova estrutura da resposta com "now_playing"
        return {
            "now_playing": {
                "song": {
                    "title": f"{artist} - {song}",
                    "artist": artist,
                    "track": song,
                    "cover": art_url
                }
            }
        }
    else:
        return {"error": "Failed to retrieve stream title"}



# Endpoint para obter informações da rádio (simplificado)
@app.get("/radio_info/")
async def get_radio_info(background_tasks: BackgroundTasks, radio_url: str):
    async with radio_data_lock:
        if radio_url not in radio_data:
            radio_data[radio_url] = {
                "song_history": [],
                "current_song": {"artist": "", "song": ""},
                "monitoring_started": False,
            }
            background_tasks.add_task(monitor_radio, radio_url, background_tasks)

        return {
            "currentSong": radio_data[radio_url]["current_song"]["song"],
            "currentArtist": radio_data[radio_url]["current_song"]["artist"],
            "songHistory": radio_data[radio_url]["song_history"],
        }
