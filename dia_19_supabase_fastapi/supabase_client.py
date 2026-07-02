
import os
from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL:
    raise ValueError("Falta SUPABASE_URL en el archivo .env")

if not SUPABASE_KEY:
    raise ValueError("Falta SUPABASE_KEY en el archivo .env")


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)
