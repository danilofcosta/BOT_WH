from typing import Any, Dict, List, Optional
from pyrogram.enums import ParseMode
from pyrogram import filters,errors

class ComandoAdmin_DevConfigs:
    def __init__(self, app, genero: str, base_data: Dict[str, Any]):
        self.genero = genero
        self.genero_txt = "ʜᴜꜱʙᴀɴᴅᴏ" if self.genero == "husbando" else "ᴡᴀɪꜰᴜ"
        self.app = app
        self.base_data = base_data
        self.ParseMode = ParseMode.HTML
        self._tk = f'{self.genero}_tk'
        Comando_check(self)
        
        #classs

    async def check_isadmin(self,client, message):
        from KEYS import DESENVOLVEDOR
        # Verificar se quem enviou o comando é admin
        if message.from_user.username == DESENVOLVEDOR.replace('@',''):
            return True
                # Obter informações do membro do grupo
        try:
            member = await self.app.get_chat_member(message.chat.id,  message.from_user.id)
        except errors.exceptions.bad_request_400.ChatAdminRequired:
            await message.reply('preciso ser adm para fazer isso :(',quote=True)

        # Verificar se o status é "administrator" ou "creator"
        if member.status.value in ("administrator", "creator",'owner'):
            return True
        return False
    


class Comando_check(ComandoAdmin_DevConfigs):
    def __init__(self, user_configs: ComandoAdmin_DevConfigs):
            # Recebe uma instância de ComandoUserConfigs para acessar os dados dela
            # super().__init__(user_configs.app, user_configs.genero, user_configs.base_data)
            user_configs.app.on_message(filters.command(["check"]))(self.Initcheck)

    async def Initcheck(self, client, message):
        
        # Verificar se o usuário é administrador
        if not await self.check_isadmin(client, message):
            return

        from BOT_HW import CONTADOR
        Infos_grupo = await CONTADOR.find_one({"group_id": message.chat.id})
        
        if not Infos_grupo:
            await message.reply("❌ Informações do grupo não encontradas no banco de dados.", quote=True)
            return
        
        txt = (
            f"🆔: {Infos_grupo['group_id']}\n"
            f"🏷 Nome: {Infos_grupo['group_name']}\n"
            f"⏲️ Num msg: {Infos_grupo['count']}\n"
            f"✅ {self.genero_txt} acertados: {len(Infos_grupo['Drops_chat_waifu_tk'])}"
        )
        
        await message.reply(txt, quote=True)

            
        

         