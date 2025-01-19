from pyrogram.enums import ParseMode
from datetime import datetime

async def enviar_midia(client, caption=None, documento=None, tipo_midia=None, idchat=int, midia=None, parse_mode=ParseMode.HTML, reply_markup=None, reply_to_message_id=None):
    if not caption:
        from . import Inline
        caption=await Inline.InlineConfig.CreateCaption(documento=documento)
        
    if documento:
        # Verifica se as chaves 'tipo', 'url' e 'file_id' existem
        tipo_midia = documento.get('tipo')
        midia = documento.get('url') or documento.get('file_id')

        # Verifique se o 'midia' foi atribuído corretamente
        if midia is None:
            print("Erro: Nenhuma URL ou file_id encontrado no documento.")
            return

    # Se o tipo de mídia for 'photo'
    if tipo_midia == 'photo':
        return await client.send_photo(chat_id=idchat, photo=midia, parse_mode=parse_mode, reply_markup=reply_markup, reply_to_message_id=reply_to_message_id, caption=caption)

    # Se o tipo de mídia for 'video'
    elif tipo_midia == 'video':
        return await client.send_video(chat_id=idchat, video=midia, parse_mode=parse_mode, reply_markup=reply_markup, reply_to_message_id=reply_to_message_id, caption=caption)

    # Se o tipo de mídia não for reconhecido, você pode levantar um erro ou exibir uma mensagem
    else:
        print("Erro: Tipo de mídia desconhecido ou não suportado.")


async def delete_messages(client, msg, ids=None):
    """
    Apaga mensagens de um chat no Telegram.

    Parâmetros:
    - client: O cliente Pyrogram usado para enviar comandos.
    - msg: A mensagem que está sendo processada.
    - ids: Um ID de mensagem único ou uma lista de IDs de mensagens a serem apagadas.
    """
    try:
        # Verifica se 'ids' é uma lista
        if isinstance(ids, list):
            await client.delete_messages(msg.chat.id, ids)
        else:
            await client.delete_messages(msg.chat.id, msg.id)
    except Exception as e:
        # Log opcional do erro para debug
        print(f"Erro ao apagar mensagem: {e}")


def criar_botoes_em_grade(dict_botoes,initcallback='', callback=None,colunas=3,b_voltar=None):
    from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
    """
    Cria uma matriz de botões organizada em uma grade com o mesmo nome e callback.

    Parâmetros:
    - lista_botoes (dict): Lista de strings com os nomes dos botões.
    - colunas (int, opcional): Número de colunas na grade. Padrão: 3.

    Retorna:
    - InlineKeyboardMarkup: Matriz de botões pronta para ser usada.
    """
    lista_botoes = []
    botoes = []
    if type(dict_botoes) == dict:
        for i in dict_botoes :lista_botoes.append(i)
    else:    
        lista_botoes = dict_botoes
    # Organiza os botões em grupos de 'colunas'
    for i in range(0, len(lista_botoes), colunas):
        linha = [
            InlineKeyboardButton(nome.title(), callback_data=initcallback+nome.lower() if not callback else callback)
            for nome in lista_botoes[i:i + colunas]
        ]
        botoes.append(linha)
    if b_voltar:
        
        botoes.append([InlineKeyboardButton('Voltar',b_voltar)])
        

    return InlineKeyboardMarkup(botoes)

async def criar_harem(id_user,first_name,Genero_bot,ID_domindo=1):
        harem = {
        "_id": id_user,
        "DATA_USER": {
            "NAME": first_name,
            "ID": id_user,
          
        },
        Genero_bot.lower(): {
            "DOMINADOS": [ID_domindo],
            "Harem": {
                "modo_harem": "padrao",
                "fav": ID_domindo
            }
        }
    }
        from . import HAREM 
        await HAREM.insert_one(harem)

def tempo_gasto(start_time):
        
        """
        Calcula o tempo decorrido desde 'start_time' até o momento atual e formata como horas, minutos e segundos.

        Args:
            start_time (datetime): O ponto no tempo do qual calcular o tempo decorrido.

        Returns:
            str: Tempo decorrido formatado como 'Xh Ym Zs'.
        """
        if not isinstance(start_time, datetime):
            raise ValueError("O parâmetro deve ser um objeto datetime.")

        tempo = int((datetime.now() - start_time).total_seconds())
        
        if tempo >= 3600:
            horas = tempo // 3600
            minutos = (tempo % 3600) // 60
            segundos = tempo % 60
            return tempo,f"{horas}h {minutos}m {segundos}s"
        elif tempo >= 60:
            minutos = tempo // 60
            segundos = tempo % 60
            return tempo,f"{minutos}m {segundos}s"
        else:
            return tempo,f"{tempo}s"
        
def to_script_text(text):
        # Dicionário para mapear letras minúsculas e maiúsculas para estilo manuscrito Unicode
        script_map = {
        'a': '𝒂', 'b': '𝒃', 'c': '𝒄', 'd': '𝒅', 'e': '𝒆', 'f': '𝒇', 'g': '𝒈',
        'h': '𝒉', 'i': '𝒊', 'j': '𝒋', 'k': '𝒌', 'l': '𝒍', 'm': '𝒎', 'n': '𝒏',
        'o': '𝒐', 'p': '𝒑', 'q': '𝒒', 'r': '𝒓', 's': '𝒔', 't': '𝒕', 'u': '𝒖',
        'v': '𝒗', 'w': '𝒘', 'x': '𝒙', 'y': '𝒚', 'z': '𝒛',
        'A': '𝑨', 'B': '𝑩', 'C': '𝑪', 'D': '𝑫', 'E': '𝑬', 'F': '𝑭', 'G': '𝑮',
        'H': '𝑯', 'I': '𝑰', 'J': '𝑱', 'K': '𝑲', 'L': '𝑳', 'M': '𝑴', 'N': '𝑵',
        'O': '𝑶', 'P': '𝑷', 'Q': '𝑸', 'R': '𝑹', 'S': '𝑺', 'T': '𝑻', 'U': '𝑼',
        'V': '𝑽', 'W': '𝑾', 'X': '𝑿', 'Y': '𝒀', 'Z': '𝒁'
    }

        
        # Converte o texto para estilo manuscrito Unicode
        return ''.join(script_map.get(char, char) for char in text)

def createBoteosvf(callv:str,callf:str):
     from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton
     keyboard = [
        [InlineKeyboardButton("❌", callback_data=callf),
           InlineKeyboardButton ("✅", callback_data=callv)
            
        ]
    ]
     return InlineKeyboardMarkup(keyboard)

def createBotao_busca_iniline(seach:str,txtbotao='🔎'):
    from pyrogram.types import InlineKeyboardMarkup,InlineKeyboardButton
    keyboard = [
        [InlineKeyboardButton(txtbotao, switch_inline_query_current_chat=seach),
   
            
        ]
    ]
    return InlineKeyboardMarkup(keyboard) 