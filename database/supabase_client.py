from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_ANON_KEY

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

supabase: Client = get_supabase_client()
