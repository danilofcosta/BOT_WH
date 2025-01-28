from pyrogram.enums import ParseMode
from typing import Any, Dict, List, Optional
from pyrogram import Client, filters
from asyncio import Lock
from BOT_HW import CONTADOR,ART_BOT
from . import uteis
from datetime import datetime
from pyrogram.types import *

import asyncio
class ContadorConfigs():
    def __init__(self, app, genero: str, base_data: Dict[str, Any]):
        self.genero = genero
        self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
        self.app = app
        self.base_data = base_data
        self.ParseMode = ParseMode.HTML
        self._tk = f'{self.genero}_tk'
        self.husbando_lock = Lock()
        self.waifu_lock = Lock()

        self.app.on_message(filters.all)(self.initContador)

    async def initContador(self,client,message):
        """Processa cada mensagem recebida no grupo."""
        if message.chat.type.value == 'private':
            return

        group_id = message.chat.id
        group_name = message.chat.title

        # Recupera ou inicializa o documento do contador para o grupo
        document = await self.initialize_or_get_group_document(group_id, group_name)

        # Incrementa o contador
        new_count = document['count'] + 1
        await CONTADOR.update_one({"group_id": group_id}, {"$set": {'count': new_count}})
        
        print(new_count, group_id,group_name)
        # Gerenciamento de locks baseado no gênero do bot
        lock = self.husbando_lock if self.genero.startswith('h') else self.waifu_lock
        
        async with lock:
            await self.handle_character_drop(document, new_count, group_id)
     
    async def handle_character_drop(self,document, new_count, group_id):
        """Gerencia o drop e a remoção de personagens."""
        drop_key = f"Drop_{self._tk}_chat"
        doprar_personagem_CONT = 100 
      
        # Drop de personagem
        if new_count % doprar_personagem_CONT == 0 and not document.get(drop_key):
            result = await self.drop_character(group_id)
            
            
            if result:
                message_id, personagem,date = result
                await CONTADOR.update_one({"group_id": group_id}, {
                    "$set": {drop_key: [message_id, personagem,date]},
                    "$push": {f'Drops_chat_{self._tk}': personagem['_id']}
                })



        # Remoção de personagem
        elif new_count % doprar_personagem_CONT == 20 and document.get(drop_key):
            await self.remove_character( group_id, document, drop_key)
        
        elif new_count >= 130:
            await CONTADOR.update_one(
                {"group_id": group_id},
                {
                    "$set": {
                        drop_key: None,
                        "count": 0
                    }
                }
            )

    async def drop_character(self,chat_id):
        """Realiza o drop de um personagem."""     
        personagem = await self.base_data.aggregate([{"$sample": {"size": 1}}]).to_list(1)
        personagem = personagem[0] if personagem else None

        if personagem:
            print(personagem.get('nome'))
            texto = await self.generate_drop_text(personagem)
            response = await uteis.enviar_midia(self.app, caption=texto, documento=personagem, idchat=chat_id)

            if response:
                #retorna o id da mendagem envida ,um dicionaro com as infos do personagem e a hora atual
                return response.id, personagem, datetime.now()

        # Retorno nulo caso algo dê errado
        return None
    async def generate_drop_text(self,personagem):
        """Gera texto de apresentação para o drop do personagem."""
        art_bot = (await ART_BOT.find_one({"arquivo": "config_geral"}))['EMOJS']

        emoji = art_bot['raridade'][personagem['raridade']]['emoji'] if personagem['evento'] == '0' else art_bot['eventos'][personagem['evento']]['emoji']

        tipo = "Uma waifu" if self.genero == "WAIFU_TK" else "Um husbando"
        return f"{emoji} <b>{tipo} Apareceu!</b>\nAdicione-o ao seu harem!\n/dominar <code>nome</code>"

    async def remove_character(self, group_id, document, drop_key):
        """Remove um personagem do chat."""

        # Validar se a chave existe
        if drop_key not in document:
            print("Erro ao remover personagem: Chave não encontrada.")
            return

        try:
            obj = document[drop_key]
            personagem = obj[1]

            # Atualizar o banco de dados
            await CONTADOR.update_one(
                {"group_id": group_id},
                {
                    "$set": {drop_key: None},
                    "$pull": {f'Drops_chat_{self._tk}': personagem['_id']}
                }
            )

            try:
                # Apagar mensagem original
                await self.app.delete_messages(int(group_id), int(obj[0]))

                # Enviar mensagem de feedback
                texto_html = (
                    f"<code>{personagem['nome']}</code> de <b>{personagem['anime']}</b> fugiu, "
                    "lembre-se do nome para dominar ele na próxima vez."
                )
                teclado = InlineKeyboardMarkup(
                    [[  
                        InlineKeyboardButton(
                            "𝑴𝒂𝒊𝒔 𝒅𝒆𝒕𝒂𝒍𝒉𝒆𝒔", 
                            switch_inline_query_current_chat=str(personagem['_id'])
                        )
                    ]]
                )
                msg = await self.app.send_message(
                    group_id, texto_html, parse_mode=self.ParseMode, reply_markup=teclado
                )

                # Aguardar antes de remover mensagem de feedback
                await asyncio.sleep(20)
                await uteis.delete_messages(self.app, msg=msg, ids=msg.id)

            except Exception as e:
                print(f"Erro ao enviar ou deletar mensagens: {e}")

        except Exception as e:
            print(f"Erro ao remover personagem: {e}")


    async def initialize_or_get_group_document(self,group_id, group_name):
            """Inicializa ou recupera o documento do grupo no banco de dados."""
            documents = await CONTADOR.find({"group_id": group_id}).to_list(length=None)

            # Remove duplicatas no banco de dados
            if len(documents) > 1:
                for doc in documents[1:]:
                    await CONTADOR.delete_one({"_id": doc["_id"]})
            document = documents[0] if documents else None
                
            if documents and document.get('count',None) is None:
                await CONTADOR.update_one({"group_id": group_id}, {"$set": {'count': 1}})
                documents = await CONTADOR.find({"group_id": group_id}).to_list(length=2)
                
            # Recupera ou cria o documento do grupo
            document = documents[0] if documents else None
            
            if not document :
                document = {
                    "group_id": group_id,
                    "group_name": group_name,
                    "count": 1,
                    "Games": {
                        'Palavra_rapida': {
                            'ativo': False,
                            'palavra': None,
                            'date': None
                        }
                    },
                    f'Drops_chat_{self._tk}': []
                }
                await CONTADOR.insert_one(document)
            
            return document
