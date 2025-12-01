from ocr.constants import GRAPHOR_BASE_URL
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def graphor_fetch(endpoint: str, **kwargs) -> dict:
    """
    Make a request to the Graphor API.
    """
    api_key = os.getenv("GRAPHORLM_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Set default timeout if not provided
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 600  # 10 minutes default for processing
    
    response = requests.post(
        f"{GRAPHOR_BASE_URL}/{endpoint}",
        headers=headers,
        **kwargs
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    return response.json()