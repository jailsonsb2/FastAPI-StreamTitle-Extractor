from fastapi import FastAPI, BackgroundTasks
from typing import Optional, Tuple, Dict, List
import urllib.request
from fastapi.middleware.cors import CORSMiddleware
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# Dicionário para armazenar o histórico por URL
history_dict: Dict[str, List[Dict[str, str]]] = {}

# Tarefa em segundo plano para monitorar a URL
def monitor_stream(url: str):
    while True:
        title = get_mp3_stream_title(url, interval=19200)  # Use um intervalo adequado
        if title:
            artist, song = extract_artist_and_song(title)
            if url in history_dict:
                history_dict[url].append({"artist": artist, "song": song})
            else:
                history_dict[url] = [{"artist": artist, "song": song}]

            # Limpar histórico após 24 horas
            now = datetime.datetime.now()
            history_dict[url] = [
                entry
                for entry in history_dict[url]
                if (now - datetime.datetime.fromisoformat(entry["timestamp"])).total_seconds()
                < 24 * 60 * 60
            ]

        # Ajuste o tempo de espera para evitar sobrecarga no servidor
        time.sleep(60)  # Verificar a cada 60 segundos


@app.get("/")
async def root():
    return {"message": "Bem vindo, estamos funcionando!"}


@app.get("/get_stream_title/")
async def read_root(url: str, interval: Optional[int] = 19200):
    title = get_mp3_stream_title(url, interval)
    if title:
        artist, song = extract_artist_and_song(title)
        return {"artist": artist, "song": song}
    else:
        return {"error": "Failed to retrieve stream title"}

def extract_artist_and_song(title: str) -> Tuple[str, str]:
    # Remove as aspas simples extras
    title = title.strip("'")
    
    if '-' in title:
        artist, song = title.split('-', 1)
        return artist.strip(), song.strip()
    else:
        return '', title.strip()
    
@app.get("/monitor_stream/")
async def monitor_stream_endpoint(url: str, background_tasks: BackgroundTasks):
    # Iniciar a tarefa em segundo plano
    background_tasks.add_task(monitor_stream, url)

    # Retornar a resposta inicial
    return {"message": "Monitoramento iniciado", "url": url}

# Endpoint para obter o histórico
@app.get("/get_history/")
async def get_history(url: str):
    if url in history_dict:
        return {
            "artist": history_dict[url][-1]["artist"],  # Artista atual
            "song": history_dict[url][-1]["song"],    # Música atual
            "history": history_dict[url][:-1],         # Histórico (excluindo a atual)
        }
    else:
        return {"error": "Histórico não encontrado para esta URL"}


