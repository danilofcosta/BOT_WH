from KEYS import MONGODB_URI,COLLECTION
from motor.motor_asyncio import AsyncIOMotorClient
Mongo = AsyncIOMotorClient(MONGODB_URI)[COLLECTION]

W_DATA=Mongo['W_DATA']
H_DATA=Mongo['H_DATA']
ART_BOT=Mongo['Configs_W-H']
HAREM=Mongo['Harem']
CONTADOR=Mongo['counters']