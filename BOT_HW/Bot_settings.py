from pyrogram import *
import asyncio,requests,tempfile
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.types import BotCommand
from pyrogram.enums import *
from KEYS import DESENVOLVEDOR,GROUP_MAIN_ID
class Settings:
    def __init__(self, app: Client, genero: str):
        self.app = app
        self.genero = genero


    def setup(self):
        """Método assíncrono que deve ser chamado após a inicialização."""
        asyncio.create_task(self.settings_commands())
        # asyncio.create_task(self.settings_profile(photo='https://i.pinimg.com/736x/48/20/b4/4820b425d82a1120653031c20d8d3878.jpg') )


    async def settings_commands(self):
        comandos = [
            {"command": f"myinfo{self.genero[0]}", "description": "Minhas informações"},
             {"command": f"top{self.genero[0]}", "description": "ranking global"},
             {"command": f"fav{self.genero[0]}", "description": "tornar favorito"},
             {"command": f"gift{self.genero[0]}", "description": "presentir"},
             {"command": f"trade{self.genero[0]}", "description": "negociar"},
             {"command": f"animelist{self.genero[0]}", "description": "Animes listados"},
        ]
        comandosset=[]
        for i in comandos:
             comandosset.append(BotCommand(i.get("command"), i.get("description",'')))

        comandosset.append(BotCommand('dominar', 'Dominar personagem'))      
        try:
            await self.app.set_bot_commands(comandosset)
        except Exception as e:
            print(e)



    async def settings_profile(self, photo=None, video=None):
        # Processamento da foto
        if photo is not None:
            if isinstance(photo, str) and (photo.startswith('http') or photo.startswith('https')):
                # Obter a foto a partir de uma URL
                response = requests.get(photo)
                if response.status_code == 200:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                            temp_file.write(response.content)
                            temp_filename = temp_file.name  # Nome do arquivo temporário
                            photo = open(temp_filename, 'rb')
            elif isinstance(photo, bytes):
                # Foto já é em bytes
                pass
            else:
                # Se foto não for uma URL nem bytes, você pode lidar com outros tipos de entrada
               
                file = await self.app.download_media(photo, in_memory=True)

                photo = file

        # Processamento do vídeo
        if video is not None:
            if isinstance(video, str) and (video.startswith('http') or video.startswith('https')):
                # Obter o vídeo a partir de uma URL
                response = requests.get(video)
                if response.status_code == 200:
                    video = response.content
            elif isinstance(video, bytes):
                # Vídeo já é em bytes
                pass
            else:
                # Se vídeo não for uma URL nem bytes, você pode lidar com outros tipos de entrada
                video= await self.app.download_media(photo, in_memory=True)
# e um file id
        try:
            # Enviar foto ou vídeo para o chat
            check = await self.app.set_profile_photo(
             
                photo=photo,
                video=video
            )
            print(check,"check")
            return check
        
        except Exception as e:
            print(f"Erro: {e}")


class BotWHConfigs(Settings):
    def __init__(self, app: Client, genero: str):
        super().__init__(app, genero)  
        print(f'profile{self.genero[0]}')
        self.app.on_message(filters.command(f'profile{self.genero[0]}', case_sensitive=False, prefixes=['/', '!', '.']))(self.Newprofile) 
    async def checkAdmSupremo(self,client, message):
        if message.from_user.username == DESENVOLVEDOR.replace('@',''): 
            return True
        try:
            async for m in self.app.get_chat_members(chat_id=GROUP_MAIN_ID, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                    if m.user.id == message.from_user.id:
                        return True
        except ChatAdminRequired:
            await message.reply('preciso ser adm para fazer isso :(',quote=True)
        except Exception as e:  
            print(e)
            return False
        # if member.status.value in ("administrator", "creator",'owner'):
        #     return True
        return False
    async def Newprofile(self, client, message):
        
        if not await self.checkAdmSupremo(client, message): 
            return await message.reply('preciso ser adm para fazer isso :(',quote=True)
        if message.reply_to_message:
            if not message.reply_to_message.photo and not message.reply_to_message.video:
                return await message.reply('Responda a mensagem do personagem que deseja Adicionar ao perfil do bot',quote=True)
            settings_profile = await Settings(self.app, self.genero).settings_profile(photo=message.reply_to_message.photo.file_id, video=None if not message.reply_to_message.video else message.reply_to_message.video.file_id)
            if settings_profile :
                await message.reply('Novo Perfil Adicionado ao bot',quote=True)
            else:
                await message.reply('Ocorreu um erro ao adicionar o novo perfil ao bot',quote=True)

        else:
            await message.reply(f'use em RESPONDA a foto quer add ao perfil do bot',quote=True)
            
            
