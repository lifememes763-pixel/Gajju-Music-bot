from pyrogram.enums import ParseMode
from SHUKLAMUSIC import app
from SHUKLAMUSIC.utils.database import is_on_off
from config import LOGGER_ID


async def play_logs(message, streamtype):
    if not await is_on_off(2):
        return

    # Safe values
    chat = message.chat
    user = message.from_user

    chat_id = chat.id
    chat_name = chat.title or "Private Chat"
    chat_username = f"@{chat.username}" if chat.username else "None"

    if user:
        user_id = user.id
        user_name = user.mention or "Unknown"
        username = f"@{user.username}" if user.username else "None"
    else:
        user_id = "Unknown"
        user_name = "Unknown"
        username = "None"

    # Safe query extraction
    query = ""
    if message.text:
        parts = message.text.split(None, 1)
        if len(parts) > 1:
            query = parts[1].strip()

    if not query:
        query = "No query provided"

    logger_text = f"""
<b>{app.mention} ᴘʟᴀʏ ʟᴏɢ</b>

<b>ᴄʜᴀᴛ ɪᴅ :</b> <code>{chat_id}</code>
<b>ᴄʜᴀᴛ ɴᴀᴍᴇ :</b> {chat_name}
<b>ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ :</b> {chat_username}

<b>ᴜsᴇʀ ɪᴅ :</b> <code>{user_id}</code>
<b>ɴᴀᴍᴇ :</b> {user_name}
<b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}

<b>ǫᴜᴇʀʏ :</b> {query}
<b>sᴛʀᴇᴀᴍᴛʏᴘᴇ :</b> {streamtype}
"""

    if chat_id != LOGGER_ID:
        try:
            await app.send_message(
                chat_id=LOGGER_ID,
                text=logger_text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except Exception:
            pass
