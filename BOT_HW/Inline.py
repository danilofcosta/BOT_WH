from pyrogram.enums import ParseMode
from pyrogram.types import *
from BOT_HW import ART_BOT,HAREM
from. import uteis
class InlineConfig:
    def __init__(self, app, genero, base_data):
        self.genero = genero
        self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
        self.app = app
        self.base_data = base_data
        self.ParseMode=ParseMode.HTML

        self.app.on_inline_query()(self.startInlineQuery)


    async def startInlineQuery(self,client, inline_query,switch_pm_text=None,limite=10,user=None):
        offset = int(inline_query.offset) if inline_query.offset else 0
        # print(offset,inline_query.offset)
        if inline_query.query == '':

            dadosresult = await self.base_data.find({}).skip(offset).sort('_id', -1).limit(limite).to_list(length=limite)

            switch_pm_text='𝕯𝖔𝖒𝖎𝖓𝖆𝖙𝖎𝖔𝖓𝕾'
        elif 'user.harem.' in inline_query.query:
            try:
                iduser = int(inline_query.query.strip().split('.')[-1])
                user=''
                try:
                    user = await self.app.get_users(iduser)
                    user=user.mention
                except Exception as error:
                    user =False
                  

           
                # Recupera os dados do harém para o usuário
                harems_cursor = HAREM.find({"_id": iduser})
                harems = await harems_cursor.to_list(length=None)
                
                if not harems:
                    return
                if not user :
                    user=harems[0]['DATA_USER']['NAME']
                    user=f'<a href=tg://user?id={iduser}>{user}</a>'
                myharem_waifu = harems[0][self.genero+'_tk']['DOMINADOS']
                dadosresult = await self.base_data.find({'_id': {'$in': myharem_waifu}}).skip(offset).limit(limite).to_list(length=limite)
                switch_pm_text=f'{self.genero_txt}: {len(myharem_waifu)}'
                
                
                
            except Exception as e:
                print(f"Erro ao processar o harém: {e}")
                return
        elif inline_query.query.strip().isdigit():
            dadosresult = await self.base_data.find({'_id': int(inline_query.query.strip())}).skip(offset).limit(limite).to_list(length=limite)
        
        else:
            var = str(inline_query.query.strip())
            dadosresult = await self.base_data.find({
            '$or': [
                {'nome': {'$regex': var, '$options': 'i'}},
                {'anime': {'$regex': var, '$options': 'i'}},
                {'categoria': {'$regex': var, '$options': 'i'}},
                {'raridade': {'$regex': var, '$options': 'i'}},
                {'tipo': {'$regex': var, '$options': 'i'}} ]
        }).skip(offset).limit(limite).to_list(length=limite)
            if not dadosresult:
                    return 



        if dadosresult: 
            results = await self.create_inline_results(dadosresult,user=user)
            await self.wiews_resuts(inline_query,results,switch_pm_text=switch_pm_text,offset=offset,lim=limite)
        

    async def create_inline_results(self,dadosresult,parsemode=ParseMode.HTML,user=None):
        """Cria resultados inline a partir dos dados recebidos."""
        objects = []
        for num,documento in enumerate(dadosresult,start=1):
            tipo = documento.get('tipo')
            fileid = documento.get('file_id')
            url = documento.get('url')


            
            # Remover as aspas simples para chamar a função corretamente
            
            caption =await self.CreateCaption(documento,user=user)
        

            # print(documento.get('_id'))
            if tipo == 'photo':
                if url:
                    result = InlineQueryResultPhoto(
                        photo_url=url,
                        caption=caption,description=caption,
                        parse_mode=parsemode,title=f"{documento.get('nome')} - {documento.get('anime')}"
                    )
                    objects.append(result)
                elif fileid:
                    result = InlineQueryResultCachedPhoto(
                        photo_file_id=fileid,
                        caption=caption,description=caption,
                        parse_mode=parsemode,title=f"{documento.get('nome')} - {documento.get('anime')} "
                    )
                    objects.append(result)
            elif tipo == 'video':
                if url:
                    result = InlineQueryResultVideo(thumb_url=url,title=f"{documento.get('nome')} - {documento.get('anime')} ",
                        video_url=url,
                        caption=caption,description=caption,
                        parse_mode=parsemode
                    )
                elif fileid:
                    result = InlineQueryResultCachedVideo(
                        video_file_id=fileid,
                        caption=caption,description=caption,
                        parse_mode=parsemode,title=f"{documento.get('nome')} - {documento.get('anime')}"
                    )

                objects.append(result)
            else:
                print(f"Tipo de mídia inválido: {tipo}")
            
        return objects
    
    async def wiews_resuts(self,inline_query,results,lim:int,offset:int,switch_pm_text:int=None):
        try:
            if not switch_pm_text:
                switch_pm_text=self.genero_txt
            next_offset = str(offset + lim) if len(results)==lim else ''
            
            
            await self.app.answer_inline_query(
                inline_query.id,
                results=results,
                next_offset=next_offset,
                is_gallery=True,
                cache_time=0,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter='x'
            )
        except Exception as e:
            print(f"Erro ao responder consulta inline: {e}")

    async def CreateCaption(self,documento,user=None):
        
        # Crie a legenda da mídia aqui
        emojs= await ART_BOT.find_one({"arquivo": "config_geral"})
        
        raridades = emojs['EMOJS']['raridade'] # type: ignore
        midia_Eventos = emojs['EMOJS']['eventos']

        #infos do aquivo
        nome = documento['nome']
        evento = documento.get('evento')
        fonte=documento['anime']
        ID=documento['_id']
        raridade=documento['raridade']
        #********************
        if evento != '0':#caso  tiver um evento definido
            evento_dados = midia_Eventos.get(evento)
            emoj = evento_dados['emoji']
            evento_emoji = f'[{emoj}]'
            Nome_evemto=evento_dados["nome"].replace("_", " ").title()
            Nome_evemto=uteis.to_script_text(Nome_evemto)
            
            EVENTO = f'\n\n{emoj} <b> {Nome_evemto}</b>  {emoj}'
        else:
            EVENTO = evento_emoji=''
                
        emojRaridade = raridades[raridade]['emoji'] # type: ignore
        nomeRaridade = raridades[raridade]['nome']

        cabeçario= f"<b>Wow! Olha só ess{'e'if self.genero == 'husbando'else 'a'} {self.genero}!</b>\n\n" if not user else f"<b>Wow! Olha só ess{'e'if self.genero == 'husbando'else 'a'} {self.genero} de </b> {user}\n\n "
        
        caption = (   f"{cabeçario}"
        f"<b>{fonte.title()}</b>\n"
        f"<b>{ID}</b> : <b>{nome.title()}</b> {evento_emoji}\n"
        f"{emojRaridade} :  <b>{nomeRaridade.title()}</strong> {EVENTO}</b>"
        )    
        return caption
    
