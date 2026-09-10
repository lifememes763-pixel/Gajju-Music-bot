# -----------------------------------------------
# 🔸 StrangerMusic Project
# -----------------------------------------------

import asyncio

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from SHUKLAMUSIC import app
from SHUKLAMUSIC.utils.database import get_assistant
from config import OWNER_ID


OWNER_ID = int(OWNER_ID)


@app.on_message(
    filters.command("gadd")
    & filters.user(OWNER_ID)
)
async def add_allbot(client, message: Message):

    if len(message.command) != 2:
        return await message.reply(
            "**❍ ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ ғᴏʀᴍᴀᴛ.**\n\n"
            "**ᴜsᴇ:** `/gadd @Bot_username`"
        )

    bot_username = message.command[1].lstrip("@")

    try:
        userbot = await get_assistant(message.chat.id)

        bot = await app.get_users(bot_username)
        bot_id = bot.id

        progress = await message.reply(
            f"❍ **ᴀᴅᴅɪɴɢ @{bot_username} ɪɴ ᴀʟʟ ᴄʜᴀᴛs...**"
        )

        done = 0
        failed = 0

        async for dialog in userbot.get_dialogs():

            chat_id = dialog.chat.id

            # Skip this specific chat
            if chat_id == -1003374468093:
                continue

            try:
                await userbot.add_chat_members(
                    chat_id,
                    bot_id
                )

                done += 1

            except FloodWait as e:
                await asyncio.sleep(e.value)
                failed += 1

            except Exception:
                failed += 1

            try:
                await progress.edit(
                    f"**❍ ᴀᴅᴅɪɴɢ @{bot_username}**\n\n"
                    f"**➥ ᴀᴅᴅᴇᴅ ɪɴ {done} ᴄʜᴀᴛs ✔**\n"
                    f"**➥ ғᴀɪʟᴇᴅ ɪɴ {failed} ᴄʜᴀᴛs ✘**"
                )
            except Exception:
                pass

            await asyncio.sleep(3)

        await progress.edit(
            f"**❍ @{bot_username} ʙᴏᴛ ᴀᴅᴅɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ 🎉**\n\n"
            f"**➥ ᴀᴅᴅᴇᴅ ɪɴ {done} ᴄʜᴀᴛs ✅**\n"
            f"**➥ ғᴀɪʟᴇᴅ ɪɴ {failed} ᴄʜᴀᴛs ✘**"
        )

    except Exception:
        await message.reply(
            "❌ **Unable to process the request.**"
        )
