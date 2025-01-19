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
        self.ComandoFav = ComandoFav(self)
        self.ComandoGift = ComandoGift(self)
        self.trade=ComandoTrade(self)
        self.ComandoAnimeList=ComandoAnimeList(self)
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
            self.app.on_message(filters.command(commands=[f'{self.genero[0]}top','top'], case_sensitive=False, prefixes=['/', '!', '.']))(self.InitTop)

            self.rk = TTLCache(maxsize=1000, ttl=300)
            self.app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("topchat_") or query.data.startswith("topglobaleu_") or query.data.startswith("topchateu_") or query.data.startswith("clear_msg")))(self.top_callback)
   
    async def InitTop(self, client, message):
        if message.command[0] == f'top' and f'@' not in message.text.lower() and message.chat.type.value != "private":
            return print(message.command[0] )
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
                [InlineKeyboardButton("𝖊𝖚", callback_data=f"topglobaleu_{message.from_user.id}")],
                    [InlineKeyboardButton("𝖙𝖔𝖕 𝖈𝖍𝖆𝖙", callback_data="topchat_"   if message.chat.type.value != "private" else "nopp")],
                      [InlineKeyboardButton("🗑", callback_data="clear_msg" )]

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
        if not self.rk.get(str(query.message.chat.id)) and not query.data.startswith("clear_msg") :
             return await query.answer("cache vazio manda /top novamente")
        if query.data.startswith("topchat_") and self.rk.get(str(query.message.chat.id)):
            num = 1
            cap = [f'\tᴛᴏᴘ {query.message.chat.title}', f'{"_" * 20}']
            ranking_total = self.rk[str(query.message.chat.id)]['RankingTotal']
            valores_adicionados = set()  # Conjunto para evitar duplicados.

            async for membro in client.get_chat_members(query.message.chat.id):
                if membro.user.id in ranking_total:
                    dados_usuario = ranking_total[membro.user.id]
                    
                    # Adiciona ao ranking apenas se não for duplicado.
                    if dados_usuario["total"] not in valores_adicionados:
                        valores_adicionados.add(dados_usuario["total"])
                        cap.append(
                            f'{num}° - <a href=tg://user?id={membro.user.id}>{dados_usuario["nome"]}</a> - <code>{dados_usuario["total"]}</code>'
                        )
                        num += 1

                # Para após o Top 10.
                if num > 10:
                    self.rk[str(query.message.chat.id)]['posiçao_user'] = num
                    break

            if isinstance(cap, list):
                cap.append(f'{"_" * 20}')
                cap = "\n".join(cap)

            keyboard = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("𝖊𝖚", callback_data=f"topchateu_{query.from_user.id}")],
                    [InlineKeyboardButton("🗑", callback_data="clear_msg" if query.message.chat.type.value != "private" else "nopp")],
                ]
            )

            await query.message.edit_text(cap, parse_mode=self.ParseMode, reply_markup=keyboard)


        elif query.data.startswith("topchateu_") and self.rk[str(query.message.chat.id)]:
            if query.message.chat.type.value == "private":
                return await query.answer("esse comando só funciona em grupos")
            
            # Recupera o ranking do cache
            ranking_total = self.rk[str(query.message.chat.id)]['RankingTotal']

            # Verifica se o usuário está no ranking
            user_data = ranking_total.get(query.from_user.id)
            if user_data:
                posicao = user_data["posicao"]
                total_dominados = user_data["total"]
                return await query.answer(f"sua posição é {posicao}° com {total_dominados} {self.genero_txt} dominados")
            
            # Caso o usuário não esteja no ranking
            await query.answer("você não está no ranking")


        elif query.data.startswith("topglobaleu_") and self.rk[str(query.message.chat.id)]:
            ps=self.rk[str(query.message.chat.id)].get('posiçao_user',None)
            if ps:
                await query.answer(f"sua posição é {ps['posicao']}° com {ps['total']} {self.genero_txt} dominados")
            else:            
                await query.answer("você não está no ranking")
        elif query.data.startswith("clear_msg"): 
            try :  
                await uteis.delete_messages(client, query.message)
                del self.rk[str(query.message.chat.id)]

            except Exception as e:  
                await query.answer("erro ao deletar mensagem")

class ComandoFav(ComandoUserConfigs):
    def __init__(self, user_configs: ComandoUserConfigs):
            # Recebe uma instância de ComandoUserConfigs para acessar os dados dela
            self.genero = user_configs.genero
            self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
            self.app = user_configs.app
            self.base_data = user_configs.base_data
            self._tk=user_configs._tk   
            self.ParseMode = ParseMode.HTML
            self.app.on_message(filters.command(commands=[f'fav',f'{self.genero[0]}fav'], case_sensitive=False, prefixes=['/', '!', '.']))(self.InitFav)

            self.rk = TTLCache(maxsize=1000, ttl=300)
            self.app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("fav_") or query.data.startswith("unfav_")))(self.fav_callback)
    async def InitFav(self, client, message):
        if message.command[0] == f'fav' and f'@' not in message.text.lower() and message.chat.type.value != "private":
                return
        if len(message.command) == 1:
            return await message.reply(f"Me o ID do {self.genero_txt} também 🤖", quote=True)
        query = {
                "_id": message.from_user.id,
                f"{self.genero}_tk.DOMINADOS": { "$elemMatch": { "$eq": message.command[1] } }
            }

        # Executar a consulta
        result = HAREM.find_one(query)

        if not result:
            return await message.reply(f"Você não tem esse {self.genero_txt} no seu harem.", quote=True)
        else:
            fav=await self.base_data.find_one({"_id":int( message.command[1])})

            keyboard = [
                [
                    InlineKeyboardButton("✅", callback_data=f"fav_{message.command[1]}_{message.from_user.id}"),
                    InlineKeyboardButton("❌", callback_data=f"unfav_{message.command[1]}_{message.from_user.id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            txt=f'Tornar seu favorito?\n  <code>☛ {fav["nome"]}-{fav["anime"]}</code>'

            await uteis.enviar_midia(self.app,idchat=message.chat.id,documento=fav,caption=txt,reply_markup=reply_markup)

    async def fav_callback(self, client, query):
        try:
            # Extrair dados do callback_data
            f, id, user = query.data.split("_")
            id = int(id)  # Converter ID para inteiro
            user = int(user)  # Converter usuário para inteiro

            # Verificar se o usuário atual é o mesmo do callback
            if query.from_user.id != user:
                return await query.answer("Você não pode fazer isso", show_alert=True)

            if f == "fav":
                # Atualizar o favorito no banco de dados
                result = await HAREM.update_one(
                    {"_id": user},
                    {"$set": {f"{self._tk}.Harem.fav": id}}
                )

                # Verificar se a atualização foi bem-sucedida
                if result.modified_count > 0:
                    await query.answer("Foi feito seu favorito")
                    await query.edit_message_caption(
                        f"Confirme seu favorito 🤖\n\n<I>/myharem{self.genero[0]}</I>",
                        parse_mode=self.ParseMode
                    )
                    logging.info(f"{user} definiu {id} como favorito")
                else:
                    await query.answer("Erro ao definir o favorito.", show_alert=True)
            elif f == "unfav":
                # Deletar mensagem usando uma função utilitária
                uteis.delete_messages(client, query.message)
            else:
                await query.answer("Ação inválida.", show_alert=True)
        except ValueError:
            await query.answer("Erro ao processar os dados.", show_alert=True)
        except Exception as e:
            await query.answer(f"Ocorreu um erro: {str(e)}", show_alert=True)

class ComandoGift(ComandoUserConfigs):
    def __init__(self, user_configs: ComandoUserConfigs):
            # Recebe uma instância de ComandoUserConfigs para acessar os dados dela
            self.genero = user_configs.genero
            self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
            self.app = user_configs.app
            self.base_data = user_configs.base_data
            self._tk=user_configs._tk   
            self.ParseMode = ParseMode.HTML
            self.app.on_message(filters.command(commands=[f'gift',f'{self.genero[0]}gift'], case_sensitive=False, prefixes=['/', '!', '.']))(self.InitGift)

            self.rk = TTLCache(maxsize=1000, ttl=300)
            self.app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("gift_")or   query.data.startswith("ungift")))(self.gift_callback)

    async def InitGift(self, client, message):
        if message.command[0] == f'gift' and f'@' not in message.text.lower() and message.chat.type.value != "private":
                return
        if not message.reply_to_message or message.reply_to_message.from_user.is_bot or message.reply_to_message.from_user.id == message.from_user.id:
            try  :
                if message.reply_to_message.from_user.is_bot:
                    return await message.reply("Você não pode presentear um bot.", quote=True)
            except Exception as e:
                pass
            return await message.reply("Responda a mensagem do personagem que deseja presentear.", quote=True)
        if len(message.command) == 1:
            return await message.reply(f"Me o ID do {self.genero_txt} também 🤖", quote=True)
        query = {
                "_id": message.from_user.id,
                f"{self.genero}_tk.DOMINADOS": { "$elemMatch": { "$eq": int(message.command[1]) } }
            }

        # Executar a consulta
        result = await HAREM.find_one(query)

        if not result:
            return await message.reply(f"Você não tem esse {self.genero_txt} no seu harem.", quote=True)
        else:
            fav=await self.base_data.find_one({"_id":int( message.command[1])})

            keyboard = [
                [
                    InlineKeyboardButton("✅", callback_data=f"gift_{message.command[1]}_{message.reply_to_message.from_user.id}_{message.from_user.id}_{message.reply_to_message.from_user.first_name}"),
                    InlineKeyboardButton("❌", callback_data=f"ungift_{message.command[1]}_{message.reply_to_message.from_user.id}_{message.from_user.id}_{message.reply_to_message.from_user.first_name}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            txt=f'Presentiar {message.reply_to_message.from_user.mention}?\n  <code>☛ {fav["nome"]}-{fav["anime"]}</code>\n'
            await uteis.enviar_midia(self.app,idchat=message.chat.id,documento=fav,caption=txt,reply_markup=reply_markup)

    async def gift_callback(self,client,query):
        try:
            f, id, recebeu,mandou,first_name = query.data.split("_")             
            id = int(id)  # Converter ID para inteiro
            recebeu = int(recebeu)
            mandou=int(mandou)  # Converter usuário para inteiro 

            if query.from_user.id != mandou:
                return await query.answer("Você não pode fazer isso", show_alert=True) 
            if f == "gift":
                # Atualizar o favorito no banco de dados
                check_harem = await HAREM.find({'_id': recebeu}).to_list(length=None)
                harem = check_harem[0] if check_harem else None
                if not harem:   
                    await uteis.criar_harem(
                        id_user=recebeu,
                        first_name=first_name,
                        Genero_bot=self._tk,
                        ID_domindo=id
                    )

                else:
                    result = await HAREM.update_one(
                    {"_id": recebeu},
                    {"$push": {f"{self._tk}.DOMINADOS": id}}
                )
                # Verificar se a atualização foi bem-sucedida
                #remover o id do harem do usuario que presenteou
                check_harem = await HAREM.find({'_id': mandou}).to_list(length=None)
                harem = check_harem[0] if check_harem else None
              
                if harem:
                    lista_dominados = harem.get(f"{self._tk.lower()}", {}).get("DOMINADOS", [])
                    lista_dominados.remove(id)
                    result =await HAREM.update_one(
                        {"_id": mandou},
                        {"$set": {f"{self._tk.lower()}.DOMINADOS": lista_dominados}}
                    )
                if result.modified_count > 0  :
                    await query.answer("Presenteado com sucesso")
                    await query.edit_message_caption(
                        f"Presenteado com sucesso 🤖\n\n<I>/myharem{self.genero[0]}</I>",
                        parse_mode=self.ParseMode
                    )
                    
                    try:
                        await self.app.send_message(
                                                                    chat_id=recebeu,  # Certifique-se de que `recebeu` é do tipo correto
                                                                    text=(
                                                                        f"🎁 <b>Você recebeu um presente!</b> 🎉\n\n"
                                                                        f"{query.from_user.mention} enviou algo incrível para você. 💝\n\n"
                                                                        f"✨ <i>Confira agora e aproveite o presente com alegria!</i> 💌"
                                                                    ),
                                                                    parse_mode=ParseMode.HTML,
                                                                    reply_markup=uteis.createBotao_busca_iniline(seach=str(id), txtbotao="🎁 Abrir Presente")
                                                                )

                    except Exception as e:
                        print (e)
                    logging.info(f"{mandou} presenteou {recebeu} com {id}")
                else:
                    await query.answer("Erro ao presentear.", show_alert=True)


            elif f == "ungift":
                # Deletar mensagem usando uma função utilitária
                uteis.delete_messages(client, query.message)
            else:
                await query.answer("Ação inválida.", show_alert=True)   
        except ValueError:
            await query.answer("Erro ao processar os dados.", show_alert=True)       

class ComandoTrade(ComandoUserConfigs):
    def __init__(self, user_configs: ComandoUserConfigs):
            # Recebe uma instância de ComandoUserConfigs para acessar os dados dela
            self.genero = user_configs.genero
            self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
            self.app = user_configs.app
            self.base_data = user_configs.base_data
            self._tk=user_configs._tk   
            self.ParseMode = ParseMode.HTML
            self.app.on_message(filters.command(commands=[f'trade',f'{self.genero[0]}trade'], case_sensitive=False, prefixes=['/', '!', '.']))(self.InitTrade)
            self.app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("trade_") or  query.data.startswith("untrade")))(self.trade_callback)
    
    async def InitTrade(self,client,message):
        if message.command[0] == f'trade' and f'@' not in message.text.lower() and message.chat.type.value != "private":
            return
        if not message.reply_to_message or message.reply_to_message.from_user.is_bot or message.reply_to_message.from_user.id == message.from_user.id:
            try  :
                if message.reply_to_message.from_user.is_bot:
                    return await message.reply("Você não pode presentear um bot.", quote=True)
            except Exception as e:
                pass
            return await message.reply("Responda a mensagem do personagem que deseja Iniciar as negociações .", quote=True)
        if len(message.command) <= 2 :
            return await message.reply(f"Me o ID  que deseja negociar e o id do personagem que dejeva 🤖\n\n <code>/{message.command[0]} 0 1 </code>", quote=True,parse_mode=self.ParseMode)
        
  

        # Executar a consulta
        j1 = await HAREM.find_one( {
                "_id": message.from_user.id,
                f"{self.genero}_tk.DOMINADOS": { "$elemMatch": { "$eq": int(message.command[1]) } }
            })
        j2 = await HAREM.find_one( {
                "_id":message.reply_to_message.from_user.id,
                f"{self.genero}_tk.DOMINADOS": { "$elemMatch": { "$eq": int(message.command[2]) } }
            })
        if not j1:
            return  await message.reply(f"{message.from_user.mention} Não tem Esse personagem {message.command[1]}", quote=True,parse_mode=self.ParseMode)
        elif not j2:
            return await message.reply(f"{message.reply_to_message.from_user.mention} Não tem Esse personagem  {message.command[2]}", quote=True,parse_mode=self.ParseMode)
        
        documento1=await self.base_data.find_one({"_id":int( message.command[1])})
        midia1 = documento1.get('url') or documento1.get('file_id')

        documento2=await self.base_data.find_one({"_id":int( message.command[2])})
        midia2 = documento2.get('url') or documento2.get('file_id')

        

        file1=InputMediaPhoto(media=midia1) if documento1.get('tipo') == 'photo' else InputMediaVideo(midia1)
        file2=InputMediaPhoto(media=midia2) if documento2.get('tipo') == 'photo' else InputMediaVideo(midia2)
        album=[file1,file2]
        linha ='-'* 40
        reply_markup= uteis.createBoteosvf(callv=f"trade_{message.command[1]}_{message.command[2]}_{message.reply_to_message.from_user.id}_{message.from_user.id}"
                                           ,callf=f"untrade_{message.command[1]}_{message.command[2]}_{message.reply_to_message.from_user.id}_{message.from_user.id}")
        

        txt=f'{message.reply_to_message.from_user.mention},{message.from_user.mention} Quer negociar com você!\n{linha}\n<code>☛ {documento1["nome"]}-{documento1["anime"]}</code>\n{linha}\n <code>☛ {documento2["nome"]}-{documento2["anime"]}</code>\n{linha}'
        midias= await self.app.send_media_group(chat_id=message.chat.id, media=album)
        
        await midias[0].edit_caption(caption=txt,
                     reply_markup=reply_markup,parse_mode=self.ParseMode)
        
        await midias[0].reply( 'Negocio fechado?',reply_markup=reply_markup,quote=True)
        

            
            

    async def trade_callback(self,client,query):
        # Extrair dados do callback
        f, J1, J2, j2recebeu, j1mandou = query.data.split("_")

        # Converter IDs para inteiros
        J1, J2, j2recebeu, j1mandou = map(int, [J1, J2, j2recebeu, j1mandou])

        # Garantir que somente o destinatário da negociação possa interagir
        if query.from_user.id != j2recebeu:
            return await query.answer("Você não pode fazer isso.", show_alert=True)

        if f == "trade":
            # Buscar o harem de j2recebeu
            harem_j2 = await HAREM.find_one({'_id': j2recebeu})
            if not harem_j2:
                return await query.answer("Erro ao acessar os dados do usuário.", show_alert=True)

            # Atualizar lista de dominados de j2recebeu
            lista_dominados_j2 = harem_j2.get(f"{self._tk.lower()}", {}).get("DOMINADOS", [])
            if J2 not in lista_dominados_j2:
                return await query.answer("Personagem não encontrado no harem.", show_alert=True)

            lista_dominados_j2.remove(J2)
            lista_dominados_j2.append(J1)
            await HAREM.update_one(
                {"_id": j2recebeu},
                {"$set": {f"{self._tk.lower()}.DOMINADOS": lista_dominados_j2}}
            )

            # Buscar o harem de j1mandou
            harem_j1 = await HAREM.find_one({'_id': j1mandou})
            if not harem_j1:
                return await query.answer("Erro ao acessar os dados do usuário.", show_alert=True)

            # Atualizar lista de dominados de j1mandou
            lista_dominados_j1 = harem_j1.get(f"{self._tk.lower()}", {}).get("DOMINADOS", [])
            if J1 not in lista_dominados_j1:
                return await query.answer("Personagem não encontrado no harem.", show_alert=True)

            lista_dominados_j1.remove(J1)
            lista_dominados_j1.append(J2)
            await HAREM.update_one(
                {"_id": j1mandou},
                {"$set": {f"{self._tk.lower()}.DOMINADOS": lista_dominados_j1}}
            )

            # Mensagem de sucesso
            await query.answer("Negócio feito com sucesso!")
            await query.edit_message_text(
                f"Negócio realizado com sucesso! 🎉\n\n<i>Use /myharem{self.genero[0]} para ver seus personagens.</i>",
                parse_mode=self.ParseMode
            )

            # Log
            logging.info(f"Usuário {j1mandou} negociou com {j2recebeu}: {J1} <-> {J2}")

        elif f == "ungift":
        # Deletar mensagem usando uma função utilitária
            uteis.delete_messages(client, query.message)

class ComandoAnimeList(ComandoUserConfigs):
    def __init__(self, user_configs: ComandoUserConfigs):
        self.genero = user_configs.genero
        self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
        self.app = user_configs.app
        self.base_data = user_configs.base_data
        self._tk = user_configs._tk
        self.ParseMode = ParseMode.HTML
        self.catalogo ={}

        # Registra o comando para a lista de animes
        self.app.on_message(
            filters.command(
                commands=[f'{self.genero[0]}animeList', 'animeList'],
                case_sensitive=False,
                prefixes=['/', '!', '.']
            )
        )(self.InitanimeList)

         
        self.app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("page_") or  query.data.startswith("anime_") or query.data.startswith("home")))(self.animeList_callback)

    async def InitanimeList(self, client, message,isfistMsg=True):
        if  message.command:
            if message.command[0] == f'animeList' and f'@' not in message.text.lower() and message.chat.type.value != "private":
                return

        # Carrega a base de dados
        FulldataBase = await self.base_data.find({}).to_list(length=None)

        # Cria o catálogo
        c = {}
        for file in FulldataBase:
            anime = file.get('anime').replace('\n','').strip()
            id = file.get('_id')
            nome = file.get('nome').replace('\n','').strip()
        
            if anime not in c:
                c[anime] = {}
            if nome not in c[anime]:
                c[anime][nome] = [id]
            else:
                c[anime][nome].append(id)

        # Ordena o catálogo
        c=dict(sorted(c.items()))
        self.catalogo[str(message.chat.id)] =c
        # Envia a primeira página
        await self.send_anime_list(client, message, page=1,isfistMsg=isfistMsg)

    async def send_anime_list(self, client, message, page=1, MAX_BUTTONS_PER_PAGE=10,isfistMsg=False):
        if not self.catalogo[str(message.chat.id)]:
            return
        chat_id = str(message.chat.id)

        # Verifica se há catálogo para o chat atual
        if chat_id not in self.catalogo or not self.catalogo[chat_id]:
            await message.reply("Nenhum anime encontrado no catálogo.")
            return
        
        # Lista de animes no catálogo
        Listaanimes=[]
        for u in self.catalogo[chat_id]:Listaanimes.append(u)
            

        # Calcula os índices de início e fim para a página
        start_index = (page - 1) * MAX_BUTTONS_PER_PAGE
        end_index = start_index + MAX_BUTTONS_PER_PAGE

        # Pega os animes da página atual
        anime_page = Listaanimes[start_index:end_index]

        if not anime_page:
            await message.reply("Página inválida.")
            return

        # Gera os botões de anime
        buttons = [
            [InlineKeyboardButton(anime.title(), callback_data=f"anime_{anime[:50]}")]
            for anime in anime_page
        ]

        # Botões de navegação
        navigation_buttons = []
        if start_index > 0:
            navigation_buttons.append(InlineKeyboardButton("← Página Anterior", callback_data=f"page_{page - 1}"))
        if end_index < len(Listaanimes):
            navigation_buttons.append(InlineKeyboardButton("Próxima Página →", callback_data=f"page_{page + 1}"))

        if navigation_buttons:
            buttons.append(navigation_buttons)

        # Envia a mensagem com os botões
        method = message.reply if isfistMsg else message.edit_text
        await method(
            "Escolha um anime:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


    async def show_characters(self, client, message, cont, MAX_BUTTONS_PER_PAGE=10, page=1):
            if not self.catalogo.get(str(message.chat.id)):
                return
            
            chaveencontrada = None
            for key, value in self.catalogo[str(message.chat.id)].items():
                if key.startswith(cont):
                    chaveencontrada = value
                    break

            if chaveencontrada is None:
                return  # Não encontrou o conteúdo solicitado

            Listaanimes = [u for u in chaveencontrada]  # Cria uma lista a partir de chaveencontrada
            start_index = (page - 1) * MAX_BUTTONS_PER_PAGE
            end_index = start_index + MAX_BUTTONS_PER_PAGE

            anime_page = Listaanimes[start_index:end_index]
            if not anime_page:
                await message.reply("Página inválida.")
                return

            # Gera os botões de anime
            buttons = [
                [InlineKeyboardButton(person.title(), switch_inline_query_current_chat=f"{person[:25]}")]
                for person in anime_page
            ]

            # Botões de navegação
            navigation_buttons = []
            if start_index > 0:
                navigation_buttons.append(InlineKeyboardButton("← Página Anterior", callback_data=f"page_{page - 1}"))
            if end_index < len(Listaanimes):
                navigation_buttons.append(InlineKeyboardButton("Próxima Página →", callback_data=f"page_{page + 1}"))

            # Adiciona os botões de navegação corretamente
            if navigation_buttons:
                buttons.append(navigation_buttons)

            # Botão de home
            buttons.append([InlineKeyboardButton("🏡", callback_data="home_home")])

            await message.edit_text(
                f"Escolha um Personagem de {key.title()}:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

       
    async def animeList_callback(self,client,query):
      
        if not self.catalogo.get(str(query.message.chat.id)):return
   
        f,cont=query.data.split('_')
        if  f == "page":
                    await self.send_anime_list(client, query.message, page=int(cont))
        elif f == "anime":
            await self.show_characters(client, query.message, cont)
        elif f == 'home':
           await  self.InitanimeList(client,  query.message,isfistMsg=False)

