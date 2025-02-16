from dotenv import load_dotenv
import os
load_dotenv()
API_HASH = os.getenv('API_HASH')
API_ID = os.getenv('API_ID')
WAIFU_TK=os.getenv('WAIFU_TK')
HUSBANDO_TK=os.getenv('HUSBANDO_TK')
BOT_TESTE = os.getenv('BOT_TESTE')
COLLECTION = os.getenv('COLLECTION')
MONGODB_URI=  os.getenv("MONGODB_URI")
GROUP_MAIN=os.getenv("GROUP_MAIN") 
GROUP_MAIN_ID=os.getenv("GROUP_MAIN_ID") 
DESENVOLVEDOR='@dog244'


if not all([API_HASH, API_ID, WAIFU_TK, HUSBANDO_TK, COLLECTION, MONGODB_URI, GROUP_MAIN]):
    raise EnvironmentError("Os valores de API_HASH, API_ID, WAIFU_TK, HUSBANDO_TK, COLLECTION, MONGODB_URI, GROUP_MAIN são Nessarios")
