import os,asyncio
from pyrogram import Client
from KEYS import API_HASH,API_ID
from pyrogram.enums import ParseMode
from BOT_HW import H_DATA,W_DATA
from . import Welcome

class BOT_WH_configs:
    def __init__(self,bot_token,NameSession='NameSession',genero='waifu',session_dir='Sessions'):
        self.genero=genero.lower()
        os.makedirs(session_dir, exist_ok=True)
        session_path = os.path.join(session_dir, NameSession)

        if NameSession not in os.listdir(session_dir):
            self.app = Client(session_path, api_id=API_ID, api_hash=API_HASH, bot_token=bot_token)
        else:
            self.app = Client(session_path)

        self.stop_event = asyncio.Event()
        
        base_data = H_DATA if   self.genero == 'husbando' else W_DATA
        #importando configuraçoes do bot
        Welcome.WelcomeConfig(self.app,self.genero,base_data)

    async def start_bot(self):
        await self.app.start()
        me = await self.app.get_me()
        print(f"{'-'*50}\n{me.username} está online\n{'-'*50} 1.0")
        
        try:
            await self.app.send_message(
                chat_id='@dog244',
                text=f"{self.genero} \n comando /start /help",
                parse_mode=ParseMode.HTML,
                disable_notification=True
            ) 
        except:
            raise ValueError('Não é possivel enviar mensagems com o bot')
        await self.stop_event.wait()

    async def stopbot(self):
        if self.app.is_connected:
            await self.app.stop()
        else:
            print("O cliente já foi encerrado.")
  
  
            
      