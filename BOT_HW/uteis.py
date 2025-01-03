from pyrogram.enums import ParseMode
async def enviar_midia(client, caption, documento=None, tipo_midia=None, idchat=int, midia=None, parse_mode=ParseMode.HTML, reply_markup=None, reply_to_message_id=None):
    
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


def criar_botoes_em_grade(lista_botoes,initcallback='', callback=None,colunas=3):
    from pyrogram.types import InlineKeyboardButton,InlineKeyboardMarkup
    """
    Cria uma matriz de botões organizada em uma grade com o mesmo nome e callback.

    Parâmetros:
    - lista_botoes (list): Lista de strings com os nomes dos botões.
    - colunas (int, opcional): Número de colunas na grade. Padrão: 3.

    Retorna:
    - InlineKeyboardMarkup: Matriz de botões pronta para ser usada.
    """
    botoes = []

    # Organiza os botões em grupos de 'colunas'
    for i in range(0, len(lista_botoes), colunas):
        linha = [
            InlineKeyboardButton(nome.lower(), callback_data=initcallback+nome.lower() if not callback else callback)
            for nome in lista_botoes[i:i + colunas]
        ]
        botoes.append(linha)
        

    return InlineKeyboardMarkup(botoes)