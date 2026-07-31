import sys
import os
import importlib.util
from colorama import init, Fore, Style

init(autoreset=True)

def print_status(component, status, message):
    if status:
        print(f"{Fore.GREEN}[OK] {component}: {message}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[FAIL] {component}: {message}{Style.RESET_ALL}")

def verify_python():
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print_status("Python", True, f"{version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_status("Python", False, f"Version {version.major}.{version.minor} is unsupported. Need 3.10+")
        return False

def verify_module(module_name, display_name=None):
    if display_name is None:
        display_name = module_name
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        print_status(display_name, True, "Installed")
        return True
    else:
        print_status(display_name, False, "Not installed. Run pip install.")
        return False

def verify_postgres():
    try:
        from sqlalchemy import create_engine
        db_url = os.getenv("DATABASE_URL", "postgresql://spiderglass:password@localhost:5432/spiderglass_db")
        # Check if we should attempt connection. SQLite is fine for fallback but user asked for Postgres check.
        if "postgresql" in db_url:
            engine = create_engine(db_url)
            connection = engine.connect()
            connection.close()
            print_status("PostgreSQL", True, "Connection successful")
        else:
            print_status("PostgreSQL", False, "DATABASE_URL is not set to a Postgres URL")
    except Exception as e:
        print_status("PostgreSQL", False, f"Connection failed: {e}")

def verify_redis():
    try:
        import redis
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.Redis.from_url(redis_url)
        r.ping()
        print_status("Redis", True, "Connection successful")
    except Exception as e:
        print_status("Redis", False, f"Connection failed: {e}")

def verify_sarvam():
    api_key = os.getenv("SARVAM_API_KEY")
    if api_key:
        print_status("Sarvam API", True, "SARVAM_API_KEY is configured")
    else:
        print_status("Sarvam API", False, "SARVAM_API_KEY is not set in environment")

def verify_jwt():
    secret = os.getenv("JWT_SECRET")
    if secret:
        print_status("JWT Config", True, "JWT_SECRET is configured")
    else:
        print_status("JWT Config", False, "JWT_SECRET is not set in environment (using default insecure secret)")

def verify_model():
    model_path = os.getenv("MODEL_PATH", "backend/models/sign_language.pt")
    if os.path.exists(model_path):
        print_status("PyTorch Model", True, f"Found at {model_path}")
    else:
        print_status("PyTorch Model", False, f"Not found at {model_path}. Inference will return MODEL_NOT_FOUND.")

if __name__ == "__main__":
    print(f"{Fore.CYAN}--- Verifying SpidyGlass Environment ---{Style.RESET_ALL}")
    verify_python()
    verify_module("pip")
    verify_module("uvicorn")
    verify_module("fastapi")
    verify_module("torch", "PyTorch")
    verify_module("mediapipe")
    
    print(f"\n{Fore.CYAN}--- Verifying Services ---{Style.RESET_ALL}")
    verify_postgres()
    verify_redis()
    
    print(f"\n{Fore.CYAN}--- Verifying Configuration ---{Style.RESET_ALL}")
    verify_sarvam()
    verify_jwt()
    verify_model()
    
    print(f"\n{Fore.CYAN}Verification complete.{Style.RESET_ALL}")
