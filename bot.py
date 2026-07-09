import sys
sys.dont_write_bytecode = True

import logging
import asyncio
from aiogram import Bot, Dispatcher, Router, F, BaseMiddleware
from aiogram.types import Message, ContentType
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config
import database
from handlers import (
    cmd_ajuda,
    cmd_start,
    welcome_new_chat,
    cmd_conquistas,
    cmd_pesar,
    on_pesar_btn_ranking,
    on_pesar_btn_perfil,
    cmd_ranking,
    cmd_resetarbct,
    cmd_doar,
    callback_dar,
    cmd_duelar,
    callback_duelo,
    cmd_injetar,
    cmd_perfil, on_perfil_btn_local, on_perfil_btn_global,
    cmd_ping,
    cmd_bctdodia,
    cmd_finalizar_temporada,
    cmd_anunciar,
    cmd_verificar_grupos,
    on_bot_chat_member,
    callback_show_achievements,
    process_achievements_callback,
    process_help_callback,
    triggers_router
)
from handlers.ranking import process_ranking_callback, process_combined_ranking_callback
from middleware.activity import ActivityMiddleware

def setup_logging():
    log_level = logging.DEBUG if getattr(config, "ENV", "prod") == "dev" else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # Silenciar libs verborrágicas mesmo em DEBUG
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("aiogram.event").setLevel(logging.INFO)
    logging.info(f"Log configurado em nível {'DEBUG' if log_level == logging.DEBUG else 'INFO'}")

def register_handlers(dp: Dispatcher):
    """Registra todos os handlers de comandos e callbacks no Aiogram 3.x."""
    router = Router()
    
    # Comandos de Mensagem
    router.message.register(cmd_start, Command('start'))
    router.message.register(cmd_pesar, Command('pesar'))
    router.message.register(cmd_ranking, Command('ranking'))

    router.message.register(cmd_resetarbct, Command('resetarbct'))
    router.message.register(cmd_conquistas, Command('conquistas'))
    router.message.register(cmd_ajuda, Command('ajuda'))
    router.message.register(cmd_doar, Command('dar'))
    router.message.register(cmd_duelar, Command('duelar'))
    router.message.register(cmd_injetar, Command('injetar', 'cheat'))
    router.message.register(cmd_perfil, Command('perfil'))
    router.message.register(cmd_ping, Command('ping'))
    router.message.register(cmd_bctdodia, Command('bctdodia'))
    router.message.register(cmd_finalizar_temporada, Command('finalizar_temporada'))
    router.message.register(cmd_anunciar, Command('anunciar'))
    router.message.register(cmd_verificar_grupos, Command('verificar_grupos'))
    router.my_chat_member.register(on_bot_chat_member)

    # Eventos de Chat (Novo membro)
    router.message.register(welcome_new_chat, F.new_chat_members)

    # Callbacks da Ajuda
    router.callback_query.register(process_help_callback, F.data.startswith('help:'))

    # Callbacks do Ranking Interativo
    router.callback_query.register(process_combined_ranking_callback, F.data.startswith('rank2:'))
    router.callback_query.register(process_ranking_callback, F.data.startswith('rank:'))
    
    # Dar (confirmação)
    router.callback_query.register(callback_dar, F.data.startswith('dar_'))

    # Duelo
    router.callback_query.register(callback_duelo, F.data.startswith('duel_'))
    
    # Conquistas
    router.callback_query.register(callback_show_achievements, F.data == 'show_achievements')
    router.callback_query.register(process_achievements_callback, F.data.startswith('achievements_page:'))

    # Callbacks dos botões rápidos do /pesar
    router.callback_query.register(on_pesar_btn_ranking, F.data.startswith('pesar_btn:ranking:'))
    router.callback_query.register(on_pesar_btn_perfil, F.data.startswith('pesar_btn:perfil:'))
    router.callback_query.register(on_perfil_btn_local, F.data.startswith('perfil_btn:local:'))
    router.callback_query.register(on_perfil_btn_global, F.data.startswith('perfil_btn:global:'))

    dp.include_router(router)
    dp.include_router(triggers_router)
    logging.debug("Handlers e Callbacks registrados com sucesso no Router 3.x.")

async def main():
    setup_logging()
    
    logging.info("Inicializando pool de conexões SQLite...")
    await database.init_pool()

    logging.info("Inicializando tabelas do banco de dados (Debug)...")
    await database.init_db()
    
    logging.info("Instanciando Bot e Dispatcher 3.x...")
    bot = Bot(token=config.API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp = Dispatcher()
    
    # Registra Middlewares
    dp.message.middleware(ActivityMiddleware())
    
    register_handlers(dp)

    logging.info("Bot online. Pressione Ctrl+C para encerrar.")
    
    # Skip updates é padrão agora, mas configurado explicitamente no Drop pending updates
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"CRASH inesperado: {e}", exc_info=True)
        try:
            await bot.send_message(config.ALLOWED_USER_ID, f"💥 <b>BOT CRASHED</b>\n\n<code>{e}</code>")
        except Exception:
            pass
        raise
    finally:
        await database.close_pool()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot finalizado manualmente.")