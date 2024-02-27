# FastAPI Metadata Stream Title Extractor

## Overview

FastAPI Stream Title Metadata Extractor is a simple application that allows users to obtain the title from the metadata of an audio stream and extract the artist and song name from it. It uses the FastAPI library to create a web API that accepts the URL of an MP3 audio stream as input and returns the artist and song name in JSON format.

## Features

- Retrieval of the title from the metadata of an audio stream
- Extraction of the artist and song name from the stream title

## Requirements

Before running the application, make sure you have the following installed:
- Python 3.x
- FastAPI
- Uvicorn

## Setup Instructions

Step 1: Clone the repository
```bash
git clone https://github.com/jailsonsb2/FastAPI_Stream_Title_metadata_Extractor.git
```
Step 2: Navigate to the project directory
```bash
cd FastAPI_Stream_Title_metadata_Extractor
```
Step 3: Create a virtual environment (optional but recommended)
```bash
python -m venv env
```
Step 4: Activate the virtual environment
- On Windows:
```bash
.\env\Scripts\activate
```
- On macOS and Linux:
```bash
source env/bin/activate
```
Step 5: Install dependencies
```bash
pip install -r requirements.txt
```
Step 6: Run the application
```bash
uvicorn main:app --reload
```

## Usage

To retrieve the title from the metadata of an audio stream, send a GET request to the '/get_stream_title/' endpoint with the 'url' parameter containing the URL of the MP3 audio stream.
```bash
http://localhost:8000/get_stream_title/?url=https://stream-172.zeno.fm/2p5tpsaurfhvv?zs=e2VhdwoXS7GcwoSTuOKJmw
```
## Contribution

Contributions are welcome! Feel free to open an issue or submit a pull request for suggestions, bug fixes, or new features.

