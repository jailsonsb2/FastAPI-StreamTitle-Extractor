# Radioplayer metadatas's Now Playng API

🚀 with Deployment Boilerplate on Digital Ocean

[![Deploy to DO](https://www.deploytodo.com/do-btn-blue.svg)](https://cloud.digitalocean.com/apps/new?repo=https://github.com/jailsonsb2/Radio-Now-Playing-API/tree/main)

Don't have an account? Get a $200 bonus to test it out!

[![DigitalOcean Referral Badge](https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%203.svg)](https://www.digitalocean.com/?refcode=54a7273746ae&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)

## Overview

This a simple application that allows users to obtain the title from the metadata of an audio stream and extract the artist and song name from it. It uses the FastAPI library to create a web API that accepts the URL of an MP3 audio stream as input and returns the artist and song name in JSON format.

This repository serves as a minimal boilerplate for deploying a FastAPI application on Digital Ocean. It's designed to provide a straightforward way to get your FastAPI application running with the least amount of headache and bloatware.

## Features

- Retrieval of the title from the metadata of an audio stream
- Extraction of the artist and song name from the stream title
- Minimal FastAPI setup
- Ready-to-deploy on Digital Ocean
- Basic configurations for a quick start

## Requirements

Before running the application, make sure you have the following installed:
- Python 3.x
- FastAPI
- Uvicorn

## Quick Start

1. Click the "Deploy to DO" button at the top.
2. Follow the instructions on Digital Ocean to deploy your app.
3. Enjoy your FastAPI app running in the cloud!

---

### Stream Title Fetcher

To retrieve the stream title and cover image, simply replace the URL parameter in the API link provided below:

**API Endpoint:** 
`https://twj.es/get_stream_title/?url=`

**Example Usage:**
Replace `https://stream.zeno.fm/yn65fsaurfhvv` with your desired stream URL:
```
https://twj.es/get_stream_title/?url=https://stream.zeno.fm/yn65fsaurfhvv
```

This will return a link to the stream’s cover image along with the title.

--- 

## Contribution

Contributions are welcome! Feel free to open an issue or submit a pull request for suggestions, bug fixes, or new features.

Happy coding! 🎉

