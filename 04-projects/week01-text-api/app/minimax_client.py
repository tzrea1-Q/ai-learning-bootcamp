import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MINIMAX_API_KEY")
BASE_URL = os.getenv("MINIMAX_BASE_URL")


def _chat_completions_url() -> str:
    if not BASE_URL:
        raise ValueError("MINIMAX_BASE_URL is not set")

    url = BASE_URL.rstrip("/")
    if url.endswith("/chat/completions"):
        return url
    return f"{url}/chat/completions"


def minimax_chat(payload: dict) -> dict:
    if not API_KEY:
        raise ValueError("MINIMAX_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.post(_chat_completions_url(), headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()
