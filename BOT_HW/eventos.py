from pyrogram.enums import ParseMode
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from BOT_HW import CONTADOR, HAREM, ART_BOT
import logging, asyncio,random
from . import uteis
from typing import Any, Dict, List, Optional
from cachetools import TTLCache
from pyrogram import Client, filters
from pyrogram.types import *  
from KEYS import GROUP_MAIN

class GerenciarEventos:
    def __init__(self, app, genero: str, base_data: Dict[str, Any]):
        self.genero = genero
        self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
        self.app = app
        self.base_data = base_data
        self.ParseMode = ParseMode.HTML
        self._tk = f'{self.genero}_tk'
        self.app.on_message(filters.new_chat_members)(self.NovoGropo)


    async def NovoGropo(self,client,message):
        for new_member in message.new_chat_members:
        
            if new_member.is_bot:
                chat_info = await client.get_chat(message.chat.id)
                group_name = chat_info.title
                num_members = await client.get_chat_members_count(message.chat.id)
                added_by = message.from_user.first_name
                welcome_text = (
                    f"Fui adicionado ao grupo '{message.chat.title}' por {added_by}.\n"
                    f"O grupo agora possui {num_members} membros.\n"
                    f"ID do chat: {message.chat.id}"
                )
                await self.app.send_message(
                chat_id=GROUP_MAIN,
                text=welcome_text,
                parse_mode=ParseMode.HTML,
                disable_notification=True
            ) 
            if num_members > 10 :
                    keyboard = [
                    [
                        InlineKeyboardButton('𝕯𝖔𝖒𝖎𝖓𝖆𝖙𝖎𝖔𝖓𝕾 𝔅�', url=GROUP_MAIN)
                    ]
                ]
                    # text='Obrigado por me adicionar no grupo ;D'
                    try:
                       
                        try:
                            await self.app.send_message(chat_id=message.from_user.id,text=f'Ei, obrigado por me adicionar no grupo {group_name}!\n',disable_notification=False,reply_markup= InlineKeyboardMarkup(keyboard))
                        except:
                            pass
                    except:
                        print('erro ao enviar mensagem')

            else:
                try:
                    text = 'Grupo tem menos de 10 membros, estou saindo.'
                    await client.send_message(message.chat.id, text=text)
                    await client.leave_chat(message.chat.id)
                    return
                except:
                    pass
       
