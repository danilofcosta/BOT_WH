from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pyrogram import Client, filters
from .uteis import enviar_midia, delete_messages,criar_botoes_em_grade
import random,json,os
from KEYS import GROUP_MAIN
from pyrogram.enums import ParseMode


class WelcomeConfig:
    def __init__(self, app, genero, base_data):
        self.genero = genero
        self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏꜱ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜꜱ"
        self.app = app
        self.base_data = base_data
        self.ParseMode=ParseMode.HTML
        # Adiciona comandos e callbacks
        self.app.on_message(filters.command(["start"]))(self.start_command)
        self.app.on_message(filters.command(["help"]))(self.welcome_callback)
        self.app.on_message(filters.command(["t"]))(self.pegar_texto)        
        #base de comandos deve receber um dict com o nome do comando e a descrição
      

        # self.app.on_callback_query()(self.callback_query)
        self.app.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("helpComandos_") or query.data in ['help','update','start']))(self.welcome_callback)

    async def start_command(self, client, message,comando=False):
        """Executa o comando /start."""
        if message.chat.type.value != "private":
            return

        loading_msg = await message.reply_text("carregando")

        try:


            me = await self.app.get_me()

            # Seleciona mídia aleatória do banco de dados
            files = await self.base_data.find({}).to_list(length=None)
            if not files:
                await message.reply_text("Nenhuma mídia encontrada no banco de dados!")
                return

            file = random.choice(files)

            # Texto de boas-vindas
            welcome_text = (
                f"<b>sᴀᴜᴅᴀçõᴇs, sᴏᴜ ᴏ <i>{me.first_name}</i>, ᴘᴀᴢᴇʀ ᴇᴍ ᴄᴏɴʜᴇᴄê-ʟᴏ(ᴀ)!</b>\n"
                "━━━━━━━▧▣▧━━━━━━━\n"
                f"<b>• ᴏ ǫᴜᴇ ᴇᴜ ғᴀçᴏ ?</b>: ᴇᴜ ɢᴇʀᴏ {self.genero_txt} "
                "ɴᴏ sᴇᴜ ɢʀᴜᴘᴏ ᴘᴀʀᴀ ǫᴜᴇ ᴏs ᴜsᴜáʀɪᴏs ᴘᴏssᴀᴍ ᴄᴀᴘᴛᴜʀá-ʟᴏ.\n"
                "━━━━━━━▧▣▧━━━━━━━"
            )


            keyboard = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("ᴀᴅᴅ+", url=f"https://t.me/{me.username}?startgroup=true")],
                    [
                        InlineKeyboardButton("ɴᴏᴛɪᴄɪᴀs/ꜱᴜᴘᴏʀᴛᴇ", url=GROUP_MAIN),
                    ],
                    [
                        InlineKeyboardButton("ᴀᴊᴜᴅᴀ", callback_data="help"),
                        InlineKeyboardButton("ᴀᴛᴜᴀʟɪᴢᴀʀ", callback_data="update"),
                    ],
                ]
            )
            if not comando and not  message.command:
                if message.photo or  message.video:
                    # Se for uma imagem com legenda
                    await message.edit_caption(welcome_text, parse_mode=self.ParseMode, reply_markup=keyboard)

            elif  comando or message.command:                
                await delete_messages(client=self.app, msg=loading_msg)
                await enviar_midia(client, caption=welcome_text, idchat=message.chat.id, documento=file, reply_markup=keyboard)

        except Exception as e:
            await message.reply_text(f"Erro: {e}")

    async def welcome_callback(self, client=None, callback_query=None,comando=False):
        """Lida com callbacks de botões inline."""
        listaDeComandos = self.LoadJson()
        try:
            try:           
                data =callback_query.command[0]
                comando=True
            except:
                data = callback_query.data

            if data.startswith("helpComandos_"):
               await self.Help_comandos(callback_query)

            elif data == "help":
                # Mensagem de ajuda
                help_text = (
                    "<b>Ajuda</b>\n\n"
                   f'''- Aqui para ajudar você a se movimentar e manter a ordem em seus grupos!\n
Tenho muitos recursos úteis, como Dopra personagems, rankings e etc.\n
Use nossos 2 bot para uma melhor exeperiencia [@Wadomination_bot | @Hudomination_bot]

Comandos úteis :
- /start : Me inicia! Você provavelmente já usou isso.
- /help : Envia esta mensagem; Vou lhe contar mais sobre mim!


Se você tiver algum bug ou dúvida sobre como me utilizar, Reporte ao @ ou em nosso grupo {GROUP_MAIN} .

Todos os comandos podem ser usados ​​com o seguinte: / !'''

                )
                if not comando:
                    keyboard = criar_botoes_em_grade(listaDeComandos,initcallback='helpComandos_',b_voltar='start')

                    if callback_query.message.photo:
                        # Se for uma imagem com legenda
                        await callback_query.message.edit_caption(help_text, parse_mode=self.ParseMode, reply_markup=keyboard)
                    else:
                        # Caso contrário, edita o texto normal
                        await callback_query.message.edit_text(help_text, parse_mode=self.ParseMode, reply_markup=keyboard)
                elif  comando:
                    keyboard = criar_botoes_em_grade(listaDeComandos,initcallback='helpComandos_')                     
                    await self.app.send_message(
                                chat_id=callback_query.chat.id,
                                text=help_text,
                                parse_mode=ParseMode.HTML,
                                reply_markup=keyboard,disable_web_page_preview=True
                            )

            elif data == "update":
                await callback_query.answer("Funcionalidade de atualização ainda não implementada!", show_alert=True)
            elif data == 'start':
                await delete_messages(client=self.app, msg=callback_query.message)
                await self.start_command(client=self.app, message=callback_query.message,comando=True)#IMITA O COMANDO /start

            else:
                await callback_query.answer("Opção desconhecida!", show_alert=True)

        except Exception as e:
            print(f"Erro no callback: {e}")


    async def Help_comandos(self, callback):
            _, comando = callback.data.split('_')

            # Definindo o glossário de comandos
            listaDeComandos = self.LoadJson()

            # Verificar se o comando existe no glossário
            if comando in listaDeComandos:
                txt = f"{listaDeComandos[comando]['texto'].replace('=',self.genero[0].lower())}"
            else:
                txt = "<b>Descrição Não Definida </b>"

            try:
                # Criar o teclado com um botão "voltar"
                keyboard = criar_botoes_em_grade(['voltar'], callback='help')

                # Editar a legenda ou o texto da mensagem com o glossário
                if callback.message.photo:
                    # Se for uma imagem com legenda
                    await callback.message.edit_caption(txt, parse_mode=self.ParseMode, reply_markup=keyboard,caption_entities =self.GerarListaEntidades(listaDeComandos[comando]['entidades']))
                else:
                    # Caso contrário, edita o texto normal
                    await callback.message.edit_text(txt, parse_mode=self.ParseMode, reply_markup=keyboard,entities =self.GerarListaEntidades(listaDeComandos[comando]['entidades']))   

            except Exception as e:
                # Caso ocorra erro ao editar a mensagem
                print(f"Erro: {e}")
                await callback.message.reply_text("Ocorreu um erro ao tentar processar seu comando.", parse_mode=self.ParseMode)


    async def pegar_texto(self, client, message):
   
        """Executa o comando /t."""
        
        # Verifica se a mensagem é uma resposta
        if not message.reply_to_message:
            await message.reply_text("Este comando deve ser usado em resposta a uma mensagem.")
            return

        # Verifica se a mensagem é um texto 
        texto = message.reply_to_message.text
        entidades = message.reply_to_message.entities
        DistEntidades = []
        if entidades:
            for num,i in enumerate(entidades):
                DistEntidades.append({'length':i.length,'offset':i.offset,
                    'type' :i.type.name})

        entidades
        msg={
            'texto':texto,
            'entidades':DistEntidades
        }
        
        try:
            arquivo_json = os.path.join("BOT_HW", "comandos.json")
            if os.path.exists(arquivo_json):
                with open(arquivo_json, 'r') as f:
                    arquivo=json.load(f) 
            else:
                arquivo={}
            arquivo[message.command[-1].strip()] = msg
            with open(arquivo_json, 'w') as f:
                json.dump(arquivo, f, indent=4)
            await message.reply_text("Texto salvo com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar no arquivo: {e}")

        


    def LoadJson(self, arquivo_json=os.path.join("BOT_HW", "comandos.json")):
        
        try:
            with open(arquivo_json, 'r',encoding='UTF-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Erro ao carregar o arquivo JSON: {e}")
            return {}
        
    def GerarListaEntidades(self, entidades):
        ListaEntidades = []
        if  entidades == None:
            return ListaEntidades
        from pyrogram.types import MessageEntity
        from pyrogram.enums import MessageEntityType
        for i in entidades:
            # Acessa o tipo da entidade diretamente pela chave do tipo (como 'SPOILER', 'BOLD', etc.)
            tipo_entidade = MessageEntityType[i['type']]
            
            # Cria a entidade com o tipo, offset e length
            entidade = MessageEntity(type=tipo_entidade, offset=i['offset'], length=i['length'])
            
            # Adiciona a entidade à lista
            ListaEntidades.append(entidade)
        
        return ListaEntidades