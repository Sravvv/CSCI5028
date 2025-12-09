import os
from dotenv import load_dotenv

load_dotenv()

def get_env(name, default=None, as_list=False):
    value = os.getenv(name, default)

    if as_list and value:
        return [item.strip() for item in value.split(",")]

    return value