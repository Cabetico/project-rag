from tqdm.auto import tqdm
from db import init_db
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("Initializing database...")
    init_db()
    
    
if __name__ == "__main__":
    main()