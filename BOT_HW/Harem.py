from pyrogram.enums import ParseMode
from pyrogram.types import *
from pyrogram import types,filters
from BOT_HW import ART_BOT,HAREM
from .uteis import enviar_midia,createBoteosvf
from cachetools import TTLCache


cache = TTLCache(maxsize=1000, ttl=300)

class haremConfig:
    def __init__(self, app, genero, base_data):
        self.genero = genero
        self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
        self.app = app
        self.base_data = base_data
        self.ParseMode=ParseMode.HTML
        
        self.app.on_message(filters.command(["harem",f'{self.genero[0]}h',f'myharem{self.genero[0]}',f'harem{self.genero[0]}']))(self.startHarem)
        self.app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("pH_") or query.data.startswith("apagarharem_") or query.data.startswith("apagarharem_")))(self.harem_callback)
        self.app.on_message(filters.command(["del",f'{self.genero[0]}del']))(self.apagar_idPersogem)
        self.app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("clear") or query.data.startswith("noclear") ))(self.callback_clear)


    async def startHarem(self, client, message):
        if message.command[0] == f'harem' and f'@' not in message.text.lower() and message.chat.type.value != "private":

            return 

        user_id =  message.from_user.id #ID do usuario
 
        harem = await HAREM.find({'_id':user_id}).to_list(length=None)
        harem = harem[0] if len(harem) > 0 else None
        
        # Verifica se o harem existe e se está bloqueado ou não contém o gênero do bot
        if harem is None:
            return await self.app.send_message(chat_id=message.chat.id, text='𝔳𝔬𝔠𝔢̂ 𝔫𝔞̃𝔬 𝔱𝔢𝔪 𝔲𝔪 𝔥𝔞𝔯𝔢𝔪')
        else:
            Genero_bot=self.genero+'_tk'
            # Obtém as informações do harem do usuário
            media = harem[Genero_bot]['Harem']
            modo = media.get('modo_harem')
            ListaDominados = harem[Genero_bot]['DOMINADOS']#lista de ids dominados
            if len(ListaDominados)== 0:
                return await message.reply( text='𝔳𝔬𝔠𝔢̂ 𝔫𝔞̃𝔬 𝔱𝔢𝔪 𝔲𝔪 𝔥𝔞𝔯𝔢𝔪', quote=True)

            
            #verfica se tem a midia de favorito caso n tenha coloca o ultimo dominado como favorito
            try:
                fav=harem[Genero_bot]['Harem']['fav']
            except:
                fav=harem[Genero_bot]['DOMINADOS'][-1]
                await HAREM.update_one(
                    {'_id':  message.from_user.id},
                    {'$set':{ f'{Genero_bot.lower()}.Harem.fav':fav}}
                )
            #busca infos da midia favorita no DB de inmagens/midias
            photo =  await self.base_data.find({'_id':fav}).to_list(length=None)
            
            #busca infos da midia ids dominados no DB de inmagens/midias          
            ListaDominadosInfos =  await self.base_data.find({'_id': {'$in': ListaDominados}}).to_list(length=None)
            if 'padrao' in modo:
                paginas=await self.Haremmodo_padrao(ListaDominados=ListaDominados,ListaDominadosInfos=ListaDominadosInfos)
                # keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text='🌐',switch_inline_query_current_chat=f'user.harem.{msg.from_user.id}'),]])
       
            numero_pg = len(paginas)
            # Ajuste conforme necessário, por exemplo, a página atual
      
                            # Cria o teclado inline com botões de navegação e controle
            keyboard = [
                    [
                        types.InlineKeyboardButton('🔙', callback_data=f'pH_{user_id}_0'),
                        types.InlineKeyboardButton(f'{1}/{numero_pg}', callback_data='nopp'),
                        types.InlineKeyboardButton('🔜', callback_data=f'pH_{user_id}_1')
                    ],
                    [
                        types.InlineKeyboardButton('🌐', switch_inline_query_current_chat=f'user.harem.{user_id}')

                    ],
                    [
                        types.InlineKeyboardButton('🗑', callback_data=f'apagarharem_{user_id}')
                    ]]
                
           
            mention_user=f'<a href=tg://user?id={user_id}>{message.from_user.first_name}</a>'
            # Cria o InlineKeyboardMarkup sem o argumento 'row_width'
            keyboard_markup = types.InlineKeyboardMarkup(keyboard)
            for num,i in enumerate(paginas):
                paginas[num]=f"{mention_user} ๛<code>Harem </code> ツ\n\n {i}"
            # Adiciona a mensagem ao cache
            if user_id in cache:
                del cache[user_id]
            cache[user_id] = paginas
            
            # Envia a mensagem com o teclado inline
            await enviar_midia(client=client,idchat=message.chat.id,caption=cache[user_id][0], reply_markup=keyboard_markup,documento=photo[0])


    async def Haremmodo_padrao(self, ListaDominados: list, ListaDominadosInfos: list):
        # Pré-carregar a configuração de emojis
        art_raridade_data = await ART_BOT.find_one({"arquivo": "config_geral"})
        art_raridade = art_raridade_data['EMOJS']['raridade']

        # Inicializar estruturas de dados
        animes = {}
        paginas = []
        contagem_harem = {}

        # Contar ocorrências de personagens no Harem
        for _id in ListaDominados:
            contagem_harem[_id] = contagem_harem.get(_id, 0) + 1

        # Organizar os personagens por anime
        for p in ListaDominadosInfos:
            if p['_id'] in contagem_harem:
                animes.setdefault(p['anime'], []).append(p)

        # Ordenar os animes por ordem alfabética
        animes_ordenados = sorted(animes.items())

        resultado = []
        cont = 0

        # Gerar formatação para cada anime e seus personagens
        for anime, chars in animes_ordenados:
            # Adicionar cabeçalho do anime
            total_personagens = len(chars)
            total_no_banco = await self.base_data.count_documents({'anime': anime})
            resultado.append(f"\n☛ <b>{anime.title()}</b> {total_personagens}/{total_no_banco}")
            resultado.append("✧" * 16)

            for p in chars:
                # Dados do personagem
                medalha = art_raridade.get(p['raridade'], {}).get('emoji', '❓')
                vezes_repetido = contagem_harem.get(p['_id'], 1)
                resultado.append(f"➢ ꙳ {p['_id']} ꙳ {medalha} ꙳ <b>{p['nome'].title()} </b> {vezes_repetido}x")
                
                # Gerenciar páginas
                cont += 1
                if cont >= 10:
                    paginas.append("\n".join(resultado).strip())
                    resultado.clear()
                    cont = 0
            
            # Finalizar seção do anime
            resultado.append("✧" * 16)

        # Adicionar última página se houver conteúdo restante
        if resultado:
            paginas.append("\n".join(resultado).strip())

        return paginas

    async def apagar_idPersogem(self,client,message):
        if message.command[0] == f'del' and f'@' not in message.text.lower() and message.chat.type.value != "private":return 
        
        query = {
                "_id": message.from_user.id,
                f"{self.genero}_tk.DOMINADOS": { "$elemMatch": { "$eq": int(message.command[1]) } }
            }

        # Executar a consulta
        result = await HAREM.find_one(query)
        if not result: return
        fav=await self.base_data.find_one({"_id":int( message.command[1])})

        await enviar_midia(self.app,idchat=message.chat.id,documento=fav,reply_markup=
        createBoteosvf(f'clear_{message.command[1]}_{message.from_user.id}',f'noclear_{message.command[1]}_{message.from_user.id}'))

    async def callback_clear(self,client,query):
        c,id,iduser=query.data.split('_')
        id=int(id)
        iduser=int(iduser)

        if query.from_user.id != iduser:return
        if c == "clear":
            check_harem = await HAREM.find({'_id': iduser}).to_list(length=None)
            harem = check_harem[0] if check_harem else None
            if harem:
                    lista_dominados = harem.get(f"{self._tk.lower()}", {}).get("DOMINADOS", [])
                    lista_dominados.remove(id)
                    result =await HAREM.update_one(
                        {"_id": iduser},
                        {"$set": {f"{self._tk.lower()}.DOMINADOS": lista_dominados}}
                    )
                    await  query.message.reply(f'Que pena !  Id {id} Foi removideo do seu /harem :(')
        else:
            await client.delete_messages(query.message.chat.id, query.message.id)
            return

    
    async def harem_callback(self,client, callback_query):
        data=callback_query.data

        if data.startswith("apagarharem_"):
            await client.delete_messages(callback_query.message.chat.id, callback_query.message.id)
            return
        try:
            bt, user_id, pg = callback_query.data.split('_')
            user_id = int(user_id)
            pg = int(pg)
            if user_id in cache:
                PaginasCache = cache[user_id]
                
                # Cria os botões do teclado
                keyboard = [
                    [
                        InlineKeyboardButton('🔙', callback_data=f'pH_{user_id}_{max(pg-1, 0)}'),
                        InlineKeyboardButton(f'{pg+1}/{len(PaginasCache)}', callback_data='nopp'),
                        InlineKeyboardButton('🔜', callback_data=f'pH_{user_id}_{min(pg+1, len(PaginasCache)-1)}')
                    ],
                    [
                        InlineKeyboardButton('🌐', switch_inline_query_current_chat=f'user.harem.{user_id}'),
                        InlineKeyboardButton('⏩²', callback_data=f'pH_{user_id}_{min(pg+2, len(PaginasCache)-2)}')
                    ],
                    [
                        InlineKeyboardButton('🗑', callback_data=f'apagarharem_{user_id}')
                    ]
                ]

                # Cria o InlineKeyboardMarkup
                keyboard_markup = InlineKeyboardMarkup(keyboard)
                if pg >len(PaginasCache):
                    pg =len(PaginasCache)
                # Atualiza a mensagem com uma nova legenda e o novo teclado
               

                await client.edit_message_caption(
                    chat_id=callback_query.message.chat.id,
                    message_id=callback_query.message.id,
                    caption=PaginasCache[pg],  # Ajuste o acesso ao conteúdo de `pag` para `pag[pg]`
                    reply_markup=keyboard_markup
                )
            else:
                await callback_query.answer("Usuário não encontrado no cache,use o comando novamente")
        
        except Exception as e:
            await callback_query.answer(f"Ultima pagina")