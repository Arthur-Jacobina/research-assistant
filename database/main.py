import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

def insert_paper(url: str, markdown: str):
    try:
        response = supabase.table("papers").insert({ "url": url, "markdown": markdown }).execute()
        return True
    except Exception as e:
        print(f"Error inserting paper: {e}")
        return False

def get_paper(url: str):
    try:
        response = supabase.table("papers").select("*").eq("url", url).execute()
        return response.data[0]
    except Exception as e:
        print(f"Error getting paper: {e}")
        return None