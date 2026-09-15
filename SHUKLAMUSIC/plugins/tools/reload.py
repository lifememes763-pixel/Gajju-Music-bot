# -----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Admin Cache / Reboot / Utility Tools
# -----------------------------------------------

import asyncio
import time
from os import getenv

from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from SHUKLAMUSIC import app
from SHUKLAMUSIC.core.call import SHUKLA
from SHUKLAMUSIC.misc import db
from SHUKLAMUSIC.utils.database import (
    get_assistant,
    get_authuser_names,
    get_cmode,
)
from SHUKLAMUSIC.utils.decorators import ActualAdminCB, AdminActual, language
from SHUKLAMUSIC.utils.formatters import alpha_to_int, get_readable_time
from config import BANNED_USERS, adminlist, lyrical

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN", "")
MONGO_DB_URI = getenv("MONGO_DB_URI", "")
STRING_SESSION = getenv("STRING_SESSION", "")

OWNER_IDS = [2145828547]

rel = {}


# -----------------------------------------------
# ADMIN CACHE RELOAD
# -----------------------------------------------

@app.on_message(
    filters.command(
        ["admincache", "reload", "refresh"],
        prefixes=["/", "!", "%", ",", "", ".", "@", "#"],
    )
    & filters.group
    & ~BANNED_USERS
)
@language
async def reload_admin_cache(client: Client, message: Message, _):
    try:
        chat_id = message.chat.id

        if chat_id not in rel:
            rel[chat_id] = 0
        else:
            saved = rel[chat_id]

            if saved > time.time():
                left = get_readable_time(
                    int(saved - time.time())
                )
                return await message.reply_text(
                    _["reload_1"].format(left)
                )

        adminlist[chat_id] = []

        async for user in app.get_chat_members(
            chat_id,
            filter=ChatMembersFilter.ADMINISTRATORS,
        ):
            privileges = user.privileges

            if privileges and privileges.can_manage_video_chats:
                adminlist[chat_id].append(user.user.id)

        authusers = await get_authuser_names(chat_id)

        for user in authusers:
            try:
                user_id = await alpha_to_int(user)
                adminlist[chat_id].append(user_id)
            except Exception:
                continue

        rel[chat_id] = int(time.time()) + 180

        await message.reply_text(_["reload_2"])

    except Exception:
        await message.reply_text(_["reload_3"])


# -----------------------------------------------
# REBOOT
# -----------------------------------------------

@app.on_message(
    filters.command("reboot")
    & filters.group
    & ~BANNED_USERS
)
@AdminActual
async def restartbot(client: Client, message: Message, _):
    mystic = await message.reply_text(
        _["reload_4"].format(app.mention)
    )

    await asyncio.sleep(1)

    try:
        db[message.chat.id] = []
        await SHUKLA.stop_stream_force(message.chat.id)
    except Exception:
        pass

    userbot = await get_assistant(message.chat.id)

    try:
        if message.chat.username:
            await userbot.resolve_peer(message.chat.username)
        else:
            await userbot.resolve_peer(message.chat.id)
    except Exception:
        pass

    chat_id = await get_cmode(message.chat.id)

    if chat_id:
        try:
            got = await app.get_chat(chat_id)
        except Exception:
            got = None

        userbot = await get_assistant(chat_id)

        try:
            if got and got.username:
                await userbot.resolve_peer(got.username)
            else:
                await userbot.resolve_peer(chat_id)
        except Exception:
            pass

        try:
            db[chat_id] = []
            await SHUKLA.stop_stream_force(chat_id)
        except Exception:
            pass

    return await mystic.edit_text(
        _["reload_5"].format(app.mention)
    )


# -----------------------------------------------
# SAFE /DONE
# -----------------------------------------------

@app.on_message(
    filters.command("done")
    & filters.private
    & filters.user(OWNER_IDS)
)
async def done_command(client: Client, message: Message):

    token_status = (
        "ᴘʀᴇsᴇɴᴛ"
        if BOT_TOKEN
        else "ᴍɪssɪɴɢ"
    )

    mongo_status = (
        "ᴘʀᴇsᴇɴᴛ"
        if MONGO_DB_URI
        else "ᴍɪssɪɴɢ"
    )

    session_status = (
        "ᴘʀᴇsᴇɴᴛ"
        if STRING_SESSION
        else "ᴍɪssɪɴɢ"
    )

    text = (
        "<blockquote>"
        "🌸 <b>𝐀ʟɪsᴀ 𝐂ᴏɴғɪɢ</b>\n"
        "━━━━━━━━━━━━\n"
        f"🤖 <b>ʙᴏᴛ ᴛᴏᴋᴇɴ :</b> "
        f"<code>{token_status}</code>\n"
        f"🍃 <b>ᴍᴏɴɢᴏ :</b> "
        f"<code>{mongo_status}</code>\n"
        f"🔐 <b>sᴛʀɪɴɢ sᴇssɪᴏɴ :</b> "
        f"<code>{session_status}</code>\n"
        "━━━━━━━━━━━━\n"
        "✅ <b>ᴄᴏɴғɪɢ ʟᴏᴀᴅᴇᴅ sᴀғᴇʟʏ.</b>"
        "</blockquote>"
    )

    await message.reply_text(text)


# -----------------------------------------------
# CLOSE
# -----------------------------------------------

@app.on_callback_query(
    filters.regex("^close$")
    & ~BANNED_USERS
)
async def close_menu(_, query: CallbackQuery):
    try:
        await query.answer()
        await query.message.delete()

        umm = await query.message.reply_text(
            f"ᴄʟᴏsᴇ ʙʏ : {query.from_user.mention}"
        )

        await asyncio.sleep(2)
        await umm.delete()

    except Exception:
        pass


# -----------------------------------------------
# STOP DOWNLOADING
# -----------------------------------------------

@app.on_callback_query(
    filters.regex("^stop_downloading$")
    & ~BANNED_USERS
)
@ActualAdminCB
async def stop_download(
    client: Client,
    callback_query: CallbackQuery,
    _,
):
    message_id = callback_query.message.id
    task = lyrical.get(message_id)

    if not task:
        return await callback_query.answer(
            _["tg_4"],
            show_alert=True,
        )

    if task.done() or task.cancelled():
        return await callback_query.answer(
            _["tg_5"],
            show_alert=True,
        )

    try:
        task.cancel()
        lyrical.pop(message_id, None)

        await callback_query.answer(
            _["tg_6"],
            show_alert=True,
        )

        return await callback_query.edit_message_text(
            _["tg_7"].format(
                callback_query.from_user.mention
            )
        )

    except Exception:
        return await callback_query.answer(
            _["tg_8"],
            show_alert=True,
)
