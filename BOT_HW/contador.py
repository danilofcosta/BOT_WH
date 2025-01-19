from pyrogram.enums import ParseMode
from typing import Any, Dict, List, Optional
from pyrogram import Client, filters

class ContadorConfigs():
    def __init__(self, app, genero: str, base_data: Dict[str, Any]):
        self.genero = genero
        self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
        self.app = app
        self.base_data = base_data
        self.ParseMode = ParseMode.HTML
        self._tk = f'{self.genero}_tk'

        self.app.on_message(filters.text | filters.photo | filters.video | filters.audio | filters.voice)(self.initContador)

    async def initContador(self,client,message):
        print(message.text)