import os
import time
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN')
ENV = os.getenv('ENV', 'prod')

ALLOWED_USER_ID = int(os.getenv('ALLOWED_USER_ID', 0))
GOD_MODE_GROUP_ID = int(os.getenv('GOD_MODE_GROUP_ID', 0))
DEV_GROUP_ID = int(os.getenv('DEV_GROUP_ID', 0))
CACHE_TTL = 60 * 5
BOT_START_TIME = time.time()
