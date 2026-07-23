import os

from dotenv import load_dotenv
from supabase import create_client
from supabase.client import ClientOptions


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL:
    raise ValueError(
        "SUPABASE_URL is missing from environment variables."
    )


if not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_KEY is missing from environment variables."
    )


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
    options=ClientOptions(
        flow_type="pkce",
    ),
)