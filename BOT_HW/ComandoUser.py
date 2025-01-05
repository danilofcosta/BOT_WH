from pyrogram.enums import ParseMode
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from BOT_HW import CONTADOR, HAREM, ART_BOT
import logging, asyncio,random
from . import uteis
from typing import Any, Dict, List, Optional
from cachetools import TTLCache


class ComandoUserConfigs:
    def __init__(self, app, genero: str, base_data: Dict[str, Any]):
        self.genero = genero
        self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
        self.app = app
        self.base_data = base_data
        self.ParseMode = ParseMode.HTML
        self._tk = f'{self.genero}_tk'
        #classs
        self.comando_harem = ComandoDominar(self)
        self.ComandoTop = ComandoTop(self)
        
        # Adiciona o comando "dominar"
       



class ComandoDominar(ComandoUserConfigs):
    def __init__(self, user_configs: ComandoUserConfigs):
            # Recebe uma instância de ComandoUserConfigs para acessar os dados dela
            self.genero = user_configs.genero
            self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
            self.app = user_configs.app
            self.base_data = user_configs.base_data
            self.ParseMode = ParseMode.HTML
            self._tk=user_configs._tk 
            self.app.on_message(filters.command(["dominar"]))(self.InitDominar)

    async def InitDominar(self, client, message):
        if message.chat.type.value == "private":
            await self._responder_mensagem(
                message, "Esse comando só funciona em grupos.", client
            )
            return

        # Busca informações do personagem no banco
        All_infos: List[Dict[str, Any]] = await CONTADOR.find_one({"group_id": message.chat.id})
        if not All_infos.get(f'Drop_{self.genero}_tk_chat'):
            # await self._responder_mensagem(
            #     message, "Nenhum personagem foi encontrado para esse grupo.", client
            # )
            return #Nao a personagem para ser dominada

        info_personagem = All_infos.get(f'Drop_{self.genero}_tk_chat', [{}])[1]
        if not info_personagem:
            await self._responder_mensagem(
                message, "Informações do personagem não encontradas.", client
            )
            return

        dt = message.command
        if len(dt) == 1:
            await self._responder_mensagem(
                message, "Ok, mas qual o nome do personagem?\nExemplo: <code>/dominar &lt;nome do personagem&gt;</code>", client, deletar_apos=20
            )
            return

        dt.pop(0)  # Remove o comando da lista
        if not self._validar_nome_personagem(info_personagem['nome'], dt):
            await self._responder_mensagem(
                message, "ɴᴏᴍᴇ ɪɴᴄᴏʀʀᴇᴛᴏ, ᴛᴇɴᴛᴇ ɴᴏᴠᴀᴍᴇɴᴛᴇ", client, deletar_apos=20
            )
            return

        if await self.coletar(message, info_personagem):
            caption = await self.create_txt_coletatrue(message, All_infos)
            await client.send_message(chat_id=message.chat.id, text=caption, parse_mode=self.ParseMode)
            txt = (
                f"Usuário: @{message.from_user.username or 'Desconhecido'} | "
                f"Comando: [{message.text or 'Nenhum'}] | "
                f"(ID: {message.from_user.id}) acertou o personagem no grupo: "
                f"{message.chat.title or 'Desconhecido'} | Grupo ID: {message.chat.id}"
            )
            await CONTADOR.update_one({"group_id": message.chat.id}, {"$set": {f'Drop_{self.genero}_tk_chat': None}})
            logging.info(txt)
    
    async def coletar(self, message, info_personagem: Dict[str, Any]) -> bool:
        id_user = message.from_user.id
        check_harem = await HAREM.find({'_id': id_user}).to_list(length=None)
        harem = check_harem[0] if check_harem else None
        
        ID_domindo = info_personagem['_id']

        if not harem:
            await uteis.criar_harem(
                id_user=id_user,
                first_name=message.from_user.first_name,
                Genero_bot=self._tk,
                ID_domindo=ID_domindo
            )
        elif not harem.get(self._tk.lower()):
            harem[self._tk.lower()] = {
                "DOMINADOS": [ID_domindo],
                "Harem": {"modo_harem": "padrao", "fav": ID_domindo}
            }
            await HAREM.update_one({'_id': id_user}, {'$set': harem})
        else:
            await HAREM.update_one(
                {'_id': id_user},
                {'$push': {f'{self._tk.lower()}.DOMINADOS': ID_domindo}}
            )
        return True

    async def create_txt_coletatrue(self, message, All_infos: List[Dict[str, Any]]) -> str:
        info_personagem = All_infos.get(f'Drop_{self.genero}_tk_chat', [{}])[1]
        art_bot = (await ART_BOT.find_one({"arquivo": "config_geral"})) or {}
        mention_user = f'<a href=tg://user?id={message.from_user.id}>{message.from_user.first_name}</a>'
        lg = 'ᴀ' if self.genero == "waifu" else 'ᴏ'
        cabeçario = f"<b>{mention_user} ᴠᴏᴄê ᴛᴇᴍ ᴜᴍ{'' if lg == 'ᴏ' else lg} ɴᴏᴠ{lg} {self.genero_txt}!</b>\n\n"

        raridades = art_bot.get('EMOJS', {}).get('raridade', {})
        midia_Eventos = art_bot.get('EMOJS', {}).get('eventos', {})
        evento_dados = midia_Eventos.get(info_personagem.get('evento'), {})
        evento_emoji = evento_dados.get('emoji', '')
        Nome_evemto = evento_dados.get('nome', '').replace("_", " ").title()
        Nome_evemto = uteis.to_script_text(Nome_evemto)
        EVENTO = f'\n\n{evento_emoji} <b>{Nome_evemto}</b> {evento_emoji}' if Nome_evemto else ''

        art_raridade = raridades.get(info_personagem['raridade'], {})
        tempo, str_tempo = uteis.tempo_gasto(All_infos.get(f'Drop_{self.genero}_tk_chat', [{}])[-1])

        return (
            f"{cabeçario}"
            f"<b>🎞 ɴᴏᴍᴇ: {info_personagem['nome'].title()}</b>\n"
            f"<b>📦 ꜰᴏɴᴛᴇ: {info_personagem['anime'].title()}</b>\n"
            f"<b>{art_raridade.get('emoji', '')} ʀᴀʀɪᴅᴀᴅᴇ: {art_raridade.get('nome', '').title()}</b> {evento_emoji}\n"
            f"{EVENTO}\n"
            f"⏳ ᴛᴇᴍᴘᴏ ɢᴀꜱᴛᴏ: <code>{str_tempo}</code>"
        )

    async def _responder_mensagem(self, message, texto, client, deletar_apos: Optional[int] = None):
        msg = await client.send_message(chat_id=message.chat.id, text=texto, parse_mode=self.ParseMode)
        if deletar_apos:
            await asyncio.sleep(deletar_apos)
            await uteis.delete_messages(client, msg)

    def _validar_nome_personagem(self, nome_personagem: str, argumentos: List[str]) -> bool:
        nome_lower = nome_personagem.lower().split()
        return all(arg.lower() in nome_lower for arg in argumentos)


class ComandoTop(ComandoUserConfigs):
    def __init__(self, user_configs: ComandoUserConfigs):
            # Recebe uma instância de ComandoUserConfigs para acessar os dados dela
            self.genero = user_configs.genero
            self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
            self.app = user_configs.app
            self.base_data = user_configs.base_data
            self._tk=user_configs._tk   
            self.ParseMode = ParseMode.HTML
            self.app.on_message(filters.command(commands=[f'top'], case_sensitive=False, prefixes=['/', '!', '.']))(self.InitTop)

            self.rk = TTLCache(maxsize=1000, ttl=300)
            self.app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("topchat_") or query.data.startswith("topglobaleu_") or query.data.startswith("topchateu_") or query.data.startswith("clear_msg")))(self.top_callback)
   
    async def InitTop(self, client, message):
     
        #retorna o ranking total e a posiçao do usuario |type: Dict[str, Any]
        cap=['\tᴛᴏᴘ ɢʟᴏʙᴀʟ',f'{"_"* 20}']
        RankingTotal,posiçao_user=await self.ranking_scan(message.from_user.id)
        
        self.rk[str(message.chat.id)] = {'RankingTotal':RankingTotal,'posiçao_user':posiçao_user}
        for num,i in enumerate(RankingTotal,start=1):
            cap.append(f'{num}° - <a href=tg://user?id={i}>{RankingTotal[i]["nome"]}</a> - <code>{RankingTotal[i]["total"]}</code>')
            if num==10:
                cap.append(f'{"_"* 20}')
                cap = "\n".join(cap)
                break
            

        keyboard = InlineKeyboardMarkup(
                [
                [InlineKeyboardButton("🙋‍♂️Eu", callback_data=f"topglobaleu_{message.from_user.id}")],
                    [InlineKeyboardButton("Top Chat", callback_data="topchat_"   if message.chat.type.value != "private" else "nopp")],

                ]
            )
        message_id_to_react =await uteis.enviar_midia(self.app,idchat=message.chat.id,caption=cap,documento=random.choice(await self.base_data.find({}).to_list(length=None)),reply_markup=keyboard)
            
        
    async def ranking_scan(self,target_user_id):
            from pymongo import DESCENDING 

            # Agregação para criar o ranking com base no tamanho da lista "DOMINADOS"
            pipeline = [
                {
                    "$match": {
                        f"{self._tk}.DOMINADOS": {"$exists": True, "$ne": []}
                    }
                },
                {
                    "$project": {
                        "_id": 1, "DATA_USER.NAME": 1,

                        "DATA_USER.ID": 1,  # Certifique-se de que o campo ID do usuário esteja disponível
                        "tamanho_dominados": {"$size": f"${self._tk}.DOMINADOS"}
                    }
                },
                {"$sort": {"tamanho_dominados": DESCENDING}}
            ]
            
            # Executar a agregação
            cursor = HAREM.aggregate(pipeline)
            posicao_usuario = None
            RankingTotal = {}
            index = 1

            async for documento in cursor:
                nome = documento["DATA_USER"]["NAME"]
                user_id = documento["DATA_USER"]["ID"]
                tamanho_dominados = documento["tamanho_dominados"]
                RankingTotal[user_id] = {   'nome':nome ,"posicao": index, "total": tamanho_dominados}

                # Verificar se o usuário alvo foi encontrado
                if user_id == target_user_id:
                    posicao_usuario = {"posicao": index,"total": tamanho_dominados}
                index += 1

            return RankingTotal,posicao_usuario
    
    async def top_callback(self, client, query):
        if not self.rk.get(str(query.message.chat.id)):
             return await query.answer("cache vazio manda /top novamente")
        if query.data.startswith("topchat_") and self.rk[str(query.message.chat.id)]:
                num=1
                cap=[f'\tᴛᴏᴘ {query.message.chat.title}',f'{"_"* 20}']

                
                async for membro in client.get_chat_members(query.message.chat.id):
                        if membro.user.id in self.rk[str(query.message.chat.id)]['RankingTotal']:
                            RankingTotal = self.rk[str(query.message.chat.id)]['RankingTotal'][query.from_user.id]
                            cap.append(f'{num}° - <a href=tg://user?id={num}>{RankingTotal["nome"]}</a> - <code>{RankingTotal["total"]}</code>')
                            num+=1
                        if num==10:
                            self.rk[str(query.message.chat.id)]['posiçao_user']=num
                            break


                if type(cap) == list:
                    cap.append(f'{"_"* 20}')
                    cap = "\n".join(cap)
                keyboard = InlineKeyboardMarkup(
                [
                [InlineKeyboardButton("Eu", callback_data=f"topchateu_{query.message.from_user.id}")],
                    [InlineKeyboardButton("Lixo", callback_data="clear_msg"   if query.message.chat.type.value != "private" else "nopp")],

                ]
            )
                await query.message.edit_text(cap,parse_mode=self.ParseMode,reply_markup=keyboard)


        elif query.data.startswith("topchateu_") and self.rk[str(query.message.chat.id)]:
            num=1
            async for membro in client.get_chat_members(query.message.chat.id):
                print(membro.user.id)
                if membro.user.id in self.rk[str(query.message.chat.id)]['RankingTotal'] and membro.user.id == query.from_user.id:
                    RankingTotal = self.rk[str(query.message.chat.id)]['RankingTotal'][membro.user.id]
                    return await query.answer(f"sua posição é {num}° com {RankingTotal['total']} {self.genero_txt} dominados")
              
                num+=1

            print('nada encontrado  ')

        elif query.data.startswith("topglobaleu_") and self.rk[str(query.message.chat.id)]:
            ps=self.rk[str(query.message.chat.id)]['posiçao_user']

            await query.answer(f"sua posição é {ps['posicao']}° com {ps['posicao']} {self.genero_txt} dominados")
        elif query.data.startswith("clear_msg"):    
            await uteis.delete_messages(client, query.message)
            del self.rk[str(query.message.chat.id)]
