# -----------------------------------------------
# 🔸 Queue Empty & Auto Direct Play Handler
# -----------------------------------------------
import random
from pyrogram import filters, enums
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from SHUKLAMUSIC import app

RANDOM_SONGS = [
    "Tu Mera Hai Sanam",
    "Kesariya",
    "Raataan Lambiyan",
    "Tum Hi Ho",
    "Apna Bana Le",
    "Heeriye",
    "O Bedardeya",
    "Chaleya",
    "Satranga",
    "Tere Vaaste"
]

async def send_queue_empty_msg(chat_id: int):
    """Sends stylized blockquote message when queue ends."""
    
    bot_mention = f"<a href='tg://user?id={app.id}'>𝐀ʟɪsᴀ</a>"
    
    empty_text = (
        f"<blockquote>"
        f"🎵 ╭──〔 💖 𝐐ᴜᴇᴜᴇ 𝐄ᴍᴘᴛʏ 〕\n"
        f"│\n"
        f"├ 💕 ⇛ ǫᴜᴇᴜᴇ ᴋʜᴀᴛᴀᴍ ʙᴇʙᴇꜱ!\n"
        f"├ 🎶 ⇛ ꜱᴏɴɢꜱ ᴋʜᴀᴛᴀᴍ ʜᴏ ɢᴀʏᴇ ʜᴀɪɴ, ᴄᴜᴛɪᴇ.\n"
        f"├ 💿 ⇛ ᴀᴜʀ ꜱᴜɴɴᴀ ʜᴀɪ ᴛᴏ ɴɪᴄʜᴇ ᴄʟɪᴄᴋ ᴋᴀʀᴏ.\n"
        f"│\n"
        f"🌸 ╰── 𝐏σᴡ𝛜ʀ𝛜𝛅 𝐁𝛄 {bot_mention}"
        f"</blockquote>"
    )

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="˹ᴘʟᴀʏ ϻσʀє˼",
                callback_data="auto_play_random_song",
                style=ButtonStyle.PRIMARY,
            )
        ]
    ])

    try:
        await app.send_message(
            chat_id=chat_id,
            text=empty_text,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=buttons
        )
    except Exception:
        pass


@app.on_callback_query(filters.regex("^auto_play_random_song$"))
async def play_more_button_click(client, query: CallbackQuery):
    selected_song = random.choice(RANDOM_SONGS)
    await query.answer(f"🎵 Random Song Picked: {selected_song}\nSend /play {selected_song}", show_alert=True)
    
