import os,asyncio
from BOT_HW.MainConfigs import BOT_WH_configs
from KEYS import WAIFU_TK,HUSBANDO_TK,BOT_TESTE
async def main(is_teste=False): 
    if not is_teste:
        # BOT_W = BOT_WH_configs() 
        # BOT_H = BOT_WH_configs() 

        # task1 = asyncio.create_task(BOT_W.start_bot())
        # task2 = asyncio.create_task(BOT_H.start_bot())
        # try:
        #     await asyncio.gather(task1, task2)
        # except Exception as e:
        #     print(f"Erro ao iniciar os bots: {e}")
        # finally:
        #     await BOT_W.stopbot()
        #     await BOT_H.stopbot()
        pass

    elif is_teste:
        #cria uma instancia com o bot de teste predefinido 
        TESTE = BOT_WH_configs(bot_token=BOT_TESTE,NameSession='BOT_TESTE',genero='waifu',session_dir='SessionsTeste')
         
        try:
            await asyncio.gather(asyncio.create_task(TESTE.start_bot()))
        except Exception as e:
            print(f"Erro ao iniciar os bots: {e}")
        finally:
            try:
                await TESTE.stopbot()
            except Exception as e:
                print(e)        

if __name__ == "__main__":
    try:
        # os.system('cls')
        pass
    except:
        print('Não é possivel fazer a limpeza da tela')
    asyncio.run(main(is_teste=True))
    