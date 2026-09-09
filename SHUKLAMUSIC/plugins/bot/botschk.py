import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from SHUKLAMUSIC import app
from config import OWNER_ID


BOT_LIST = [
    "MADARA_X_RAID10_BOT",
    "MADARA_X_RAID_BOT",
    "MADARA_X_RAID2_BOT",
    "MADARA_X_RAID3_BOT",
    "MADARA_X_RAID4_BOT",
]


@app.on_message(filters.command("botschk") & filters.user(OWNER_ID))
async def bots_chk(client, message):

    msg = await message.reply_photo(
        photo="https://telegra.ph/file/4d303296e4fac9a40ea07.jpg",
        caption="**ᴄʜᴇᴄᴋɪɴɢ ʙᴏᴛs sᴛᴀᴛs ᴀʟɪᴠᴇ ᴏʀ ᴅᴇᴀᴅ...**"
    )

    response = (
        "**ᴄʜᴇᴄᴋɪɴɢ ʙᴏᴛs sᴛᴀᴛs ᴀʟɪᴠᴇ ᴏʀ ᴅᴇᴀᴅ**\n\n"
    )

    for bot_username in BOT_LIST:

        try:
            # Remove @ if accidentally added
            username = bot_username.lstrip("@")

            bot = await client.get_users(username)
            bot_id = bot.id

            # Send /start to the bot
            await client.send_message(bot_id, "/start")

            # Give bot some time to respond
            await asyncio.sleep(3)

            # Check latest message
            latest_message = None

            async for bot_message in client.get_chat_history(
                bot_id,
                limit=1
            ):
                latest_message = bot_message
                break

            if (
                latest_message
                and latest_message.from_user
                and latest_message.from_user.id == bot_id
            ):
                response += (
                    f"╭⎋ [{bot.first_name}](tg://user?id={bot.id})\n"
                    f"╰⊚ **sᴛᴀᴛᴜs: ᴏɴʟɪɴᴇ ✨**\n\n"
                )
            else:
                response += (
                    f"╭⎋ [{bot.first_name}](tg://user?id={bot.id})\n"
                    f"╰⊚ **sᴛᴀᴛᴜs: ᴏғғʟɪɴᴇ ❄️**\n\n"
                )

        except FloodWait as e:
            await asyncio.sleep(e.value)

            response += (
                f"╭⎋ {bot_username}\n"
                f"╰⊚ **sᴛᴀᴛᴜs: ғʟᴏᴏᴅᴡᴀɪᴛ ⏳**\n\n"
            )

        except Exception:
            response += (
                f"╭⎋ {bot_username}\n"
                f"╰⊚ **sᴛᴀᴛᴜs: ᴇʀʀᴏʀ ❌**\n\n"
            )

    await msg.edit_caption(
        caption=response
    )
