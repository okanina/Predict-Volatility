import os
from dotenv import load_dotenv

load_dotenv(".env")

api_key:str =os.getenv("api_key")
db_name:str =os.getenv("db_name")
model_directory: str=os.getenv("model_directory")
