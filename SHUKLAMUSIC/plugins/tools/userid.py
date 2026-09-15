from SHUKLAMUSIC import app
from pyrogram import filters
from pyrogram.enums import ParseMode, ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@app.on_message(filters.command("id"))
async def getid(client, message):
    chat = message.chat
    reply = message.reply_to_message
    your_id = message.from_user.id if message.from_user else "Unknown"
    message_id = message.id

    text = (
        f"**● [ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message_id}`\n"
        f"**● [ʏᴏᴜʀ ɪᴅ:](tg://user?id={your_id})** `{your_id}`\n"
    )

    # User ID from /id username
    if len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
            user_id = user.id

            text += (
                f"**● [ᴜsᴇʀ ɪᴅ:](tg://user?id={user_id})** "
                f"`{user_id}`\n"
            )
        except Exception:
            return await message.reply_text(
                "● ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ.",
                quote=True
            )

    # Chat ID
    if chat.username:
        text += (
            f"**● [ᴄʜᴀᴛ ɪᴅ:](https://t.me/{chat.username})** "
            f"`{chat.id}`\n\n"
        )
    else:
        text += f"**● ᴄʜᴀᴛ ɪᴅ:** `{chat.id}`\n\n"

    # Replied user's ID
    if (
        reply
        and not getattr(reply, "empty", True)
        and not reply.sender_chat
        and not reply.forward_from_chat
    ):
        if reply.from_user:
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

    # Forwarded channel
    if reply and reply.forward_from_chat:
        forwarded_chat = reply.forward_from_chat

        text += (
            f"● ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, "
            f"{forwarded_chat.title}, ʜᴀs ᴀɴ ɪᴅ ᴏғ "
            f"`{forwarded_chat.id}`\n\n"
        )

    # Sender chat
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
        disable_web_page_preview=True,
        parse_mode=ParseMode.DEFAULT,
        reply_markup=buttons
    )


@app.on_callback_query(filters.regex("^close_id$"))
async def close_id_callback(client, query):
    await query.answer()
    try:
        await query.message.delete()
    except Exception:
        try:
            await query.message.edit_reply_markup(None)
        except Exception:
            pass
