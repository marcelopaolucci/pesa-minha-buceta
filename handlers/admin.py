import asyncio
import html
import logging
import random
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramRetryAfter
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import CommandObject
from aiogram.enums import ChatMemberStatus
from config import ALLOWED_USER_ID
from database import inject_weight, finalize_local_season, get_season_label, get_current_season, get_all_groups, delete_group, upsert_group
from utils import parse_weight_to_grams, format_weight
from utils.messages import Messages
from utils.emojis import Emojis
from handlers._decorators import owner_only


@owner_only(silent=False, deny_msg=Messages.Errors.INJETAR_DENIED)
async def cmd_injetar(message: Message, command: CommandObject = None):
    """/injetar [<peso>] — injeta peso no alvo (reply) ou no próprio dono. Sem args: padrão 20kg."""
    args = command.args if command else None
    try:
        amount = parse_weight_to_grams(args) if args else 20000.0
    except (ValueError, TypeError):
        await message.reply(Messages.Admin.INVALID_INJECT_VALUE, parse_mode='HTML')
        return

    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
        target_name = message.reply_to_message.from_user.first_name or "Usuário"
    else:
        target_id = message.from_user.id
        target_name = message.from_user.first_name or "Você"

    await inject_weight(target_id, message.chat.id, amount, target_name)

    formatted_kg = format_weight(amount)
    await message.reply(
        random.choice(Messages.System.INJECT_SUCCESS).format(kg=formatted_kg, name=target_name),
        parse_mode="HTML"
    )


@owner_only()
async def cmd_finalizar_temporada(message: Message):
    """/finalizar_temporada — força encerramento da temporada local: snapshot Top 3, reset peso_temporada."""
    chat_id = message.chat.id
    label = get_season_label(get_current_season())
    winners = await finalize_local_season(chat_id)

    if winners is None:
        await message.reply(Messages.Admin.SEASON_END_FAIL, parse_mode="HTML")
        return

    if not winners:
        await message.reply(Messages.Admin.SEASON_END_EMPTY, parse_mode="HTML")
        return

    text = Messages.Ranking.get_reset_announcement_msg(label, winners)
    await message.reply(text, parse_mode="HTML")


@owner_only()
async def cmd_anunciar(message: Message, command: CommandObject = None):
    """/anunciar <texto> — broadcast para todos os grupos, 1/s. Remove grupos inacessíveis."""
    text = command.args if command else None
    if not text:
        await message.reply(Messages.Admin.ANUNCIAR_USAGE, parse_mode="HTML")
        return

    groups = await get_all_groups()
    if not groups:
        await message.reply(Messages.Admin.NO_GROUPS, parse_mode="HTML")
        return

    status_msg = await message.reply(
        Messages.Admin.BROADCAST_PROGRESS.format(count=len(groups)), parse_mode="HTML"
    )

    sent = 0
    removed = 0
    failed = 0

    for chat_id, title in groups:
        try:
            await message.bot.send_message(chat_id, text, parse_mode="HTML")
            sent += 1
        except TelegramForbiddenError:
            # Bot foi removido/bloqueado do grupo
            await delete_group(chat_id)
            removed += 1
            logging.info(f"Broadcast: grupo removido do DB (Forbidden) — {chat_id} ({title})")
        except TelegramBadRequest as e:
            # Grupo inválido/migrado/deletado
            await delete_group(chat_id)
            removed += 1
            logging.info(f"Broadcast: grupo removido do DB (BadRequest: {e}) — {chat_id} ({title})")
        except TelegramRetryAfter as e:
            # Rate limit do Telegram — aguarda e retenta uma vez
            await asyncio.sleep(e.retry_after + 1)
            try:
                await message.bot.send_message(chat_id, text, parse_mode="HTML")
                sent += 1
            except Exception:
                failed += 1
        except Exception as e:
            logging.warning(f"Broadcast: falha inesperada em {chat_id}: {e}")
            failed += 1

        await asyncio.sleep(1)

    summary = Messages.Admin.BROADCAST_SUMMARY.format(
        sent=sent, removed=removed, failed=failed, total=len(groups)
    )
    await status_msg.edit_text(summary, parse_mode="HTML")


async def on_bot_chat_member(event: ChatMemberUpdated):
    """Notifica dono quando bot é adicionado ou removido de um grupo."""
    old = event.old_chat_member.status
    new = event.new_chat_member.status

    added = old in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED) and new in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR)
    removed = old in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR) and new in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)

    if not added and not removed:
        return

    chat = event.chat
    chat_link = f"@{chat.username}" if chat.username else f"<code>{chat.id}</code>"

    if added:
        await upsert_group(chat.id, chat.title, chat.username)
        text = Messages.Admin.GROUP_ADDED.format(title=html.escape(chat.title), link=chat_link)
        logging.info(f"Bot adicionado ao grupo {chat.id} ({chat.title})")
    else:
        await delete_group(chat.id)
        text = Messages.Admin.GROUP_REMOVED.format(title=html.escape(chat.title), link=chat_link)
        logging.info(f"Bot removido do grupo {chat.id} ({chat.title})")

    try:
        await event.bot.send_message(ALLOWED_USER_ID, text, parse_mode="HTML")
    except Exception as e:
        logging.warning(f"on_bot_chat_member: falha ao notificar dono — {e}")


@owner_only()
async def cmd_verificar_grupos(message: Message):
    """/verificar_grupos — verifica presença do bot em todos os grupos via get_chat_member. Remove inacessíveis."""
    groups = await get_all_groups()
    if not groups:
        await message.reply(Messages.Admin.NO_GROUPS, parse_mode="HTML")
        return

    status_msg = await message.reply(
        Messages.Admin.VERIFY_PROGRESS_HEADER.format(count=len(groups)), parse_mode="HTML"
    )

    bot_id = (await message.bot.get_me()).id

    active = 0
    removed = 0
    failed = 0
    total = len(groups)

    for i, (chat_id, title) in enumerate(groups, start=1):
        if i % 50 == 0 or i == 1:
            try:
                await status_msg.edit_text(
                    Messages.Admin.VERIFY_PROGRESS_TICK.format(
                        i=i, total=total, active=active, removed=removed, failed=failed
                    ),
                    parse_mode="HTML"
                )
            except Exception:
                pass

        attempts = 0

        while attempts < 2:
            try:
                member = await message.bot.get_chat_member(chat_id, bot_id)

                if member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
                    await delete_group(chat_id)
                    removed += 1
                    logging.info(f"Verificar: removido (status={member.status}) — {chat_id} ({title})")
                else:
                    active += 1

                break

            except TelegramRetryAfter as e:
                wait_time = e.retry_after + random.uniform(0.5, 2)
                logging.warning(f"Rate limit em {chat_id}: aguardando {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
                attempts += 1

            except TelegramForbiddenError:
                await delete_group(chat_id)
                removed += 1
                logging.info(f"Verificar: removido (Forbidden) — {chat_id} ({title})")
                break

            except TelegramBadRequest as e:
                await delete_group(chat_id)
                removed += 1
                logging.info(f"Verificar: removido (BadRequest: {e}) — {chat_id} ({title})")
                break

            except Exception as e:
                logging.warning(f"Verificar: falha inesperada em {chat_id}: {e}")
                attempts += 1
                if attempts >= 2:
                    failed += 1

        await asyncio.sleep(random.uniform(0.05, 0.1))

    summary = Messages.Admin.VERIFY_SUMMARY.format(
        active=active, removed=removed, failed=failed, total=len(groups)
    )
    await status_msg.edit_text(summary, parse_mode="HTML")
