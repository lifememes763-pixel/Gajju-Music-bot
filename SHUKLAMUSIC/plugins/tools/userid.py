from SHUKLAMUSIC import app
from pyrogram import filters
from pyrogram.enums import ParseMode, ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@app.on_message(filters.command("id"))
async def getid(client, message):
    chat = message.chat
    reply = message.reply_to_message
    your_id = message.from_user.id if message.from_user else "Unknown"

    text = (
        f"**● [ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message.id}`\n"
        f"**● [ʏᴏᴜʀ ɪᴅ:](tg://user?id={your_id})** `{your_id}`\n"
    )

    if len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
            text += (
                f"**● [ᴜsᴇʀ ɪᴅ:](tg://user?id={user.id})** "
                f"`{user.id}`\n"
            )
        except Exception:
            return await message.reply_text(
                "● ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ."
            )

    if chat.username:
        text += (
            f"**● [ᴄʜᴀᴛ ɪᴅ:](https://t.me/{chat.username})** "
            f"`{chat.id}`\n\n"
        )
    else:
        text += f"**● ᴄʜᴀᴛ ɪᴅ:** `{chat.id}`\n\n"

    if reply and not getattr(reply, "empty", True):
        if reply.from_user and not reply.sender_chat and not reply.forward_from_chat:
            text += (
                f"**● [ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:]({reply.link})** "
                f"`{reply.id}`\n"
                f"**● [ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:](tg://user?id="
                f"{reply.from_user.id})** `{reply.from_user.id}`\n\n"
            )
        else:
            text += (
                f"**● ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:** `{reply.id}`\n\n"
            )

    if reply and reply.forward_from_chat:
        forwarded_chat = reply.forward_from_chat
        text += (
            f"● ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, "
            f"{forwarded_chat.title}, ʜᴀs ᴀɴ ɪᴅ ᴏғ "
            f"`{forwarded_chat.id}`\n\n"
        )

    if reply and reply.sender_chat:
        text += (
            f"● ɪᴅ ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ, "
            f"ɪs `{reply.sender_chat.id}`"
        )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "ᴄʟᴏsᴇ",
                    callback_data="close_id",
                    style=ButtonStyle.DANGER
                )
            ]
        ]
    )

    await message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=buttons
    )


@app.on_callback_query(filters.regex(r"^close_id$"))
async def close_id_callback(client, query):
    await query.answer()

    if not query.message:
        return

    try:
        await query.message.delete()
    except Exception:
        try:
            await query.message.edit_reply_markup(None)
        except Exception:
            pass
