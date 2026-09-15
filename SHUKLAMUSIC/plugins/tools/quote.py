# -----------------------------------------------
# 🔸 Alisa x Music
# 🔹 Quote / Quotly System
# -----------------------------------------------

from io import BytesIO
from pyrogram import Client, filters
from pyrogram.types import Message
from httpx import AsyncClient, Timeout
from SHUKLAMUSIC import app


fetch = AsyncClient(
    http2=True,
    verify=True,
    headers={
        "Accept-Language": "en-US",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/107.0.0.0 Safari/537.36"
        ),
        "Content-Type": "application/json",
    },
    timeout=Timeout(20),
)


class QuotlyException(Exception):
    pass


async def get_message_sender_id(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_sender_name:
            return 1
        elif ctx.forward_from:
            return ctx.forward_from.id
        elif ctx.forward_from_chat:
            return ctx.forward_from_chat.id
        return 1

    if ctx.from_user:
        return ctx.from_user.id

    if ctx.sender_chat:
        return ctx.sender_chat.id

    return 1


async def get_message_sender_name(ctx: Message):
    if ctx.forward_date:
        if ctx.forward_sender_name:
            return ctx.forward_sender_name

        if ctx.forward_from:
            return (
                f"{ctx.forward_from.first_name} {ctx.forward_from.last_name}"
                if ctx.forward_from.last_name
                else ctx.forward_from.first_name
            )

        if ctx.forward_from_chat:
            return ctx.forward_from_chat.title

        return ""

    if ctx.from_user:
        return (
            f"{ctx.from_user.first_name} {ctx.from_user.last_name}"
            if ctx.from_user.last_name
            else ctx.from_user.first_name
        )

    if ctx.sender_chat:
        return ctx.sender_chat.title

    return ""


async def get_message_sender_username(ctx: Message):
    if ctx.forward_date:
        if (
            not ctx.forward_sender_name
            and not ctx.forward_from
            and ctx.forward_from_chat
            and ctx.forward_from_chat.username
        ):
            return ctx.forward_from_chat.username

        if (
            not ctx.forward_sender_name
            and not ctx.forward_from
            and ctx.forward_from_chat
        ) or ctx.forward_sender_name or not ctx.forward_from:
            return ""

        return ctx.forward_from.username or ""

    if ctx.from_user and ctx.from_user.username:
        return ctx.from_user.username

    if (
        ctx.from_user
        or (ctx.sender_chat and not ctx.sender_chat.username)
        or not ctx.sender_chat
    ):
        return ""

    return ctx.sender_chat.username


async def get_message_sender_photo(ctx: Message):
    if ctx.forward_date:
        if (
            not ctx.forward_sender_name
            and not ctx.forward_from
            and ctx.forward_from_chat
            and ctx.forward_from_chat.photo
        ):
            return {
                "small_file_id": ctx.forward_from_chat.photo.small_file_id,
                "small_photo_unique_id": (
                    ctx.forward_from_chat.photo.small_photo_unique_id
                ),
                "big_file_id": ctx.forward_from_chat.photo.big_file_id,
                "big_photo_unique_id": (
                    ctx.forward_from_chat.photo.big_photo_unique_id
                ),
            }

        if (
            not ctx.forward_sender_name
            and not ctx.forward_from
            and ctx.forward_from_chat
        ) or ctx.forward_sender_name or not ctx.forward_from:
            return ""

        if ctx.forward_from.photo:
            return {
                "small_file_id": ctx.forward_from.photo.small_file_id,
                "small_photo_unique_id": (
                    ctx.forward_from.photo.small_photo_unique_id
                ),
                "big_file_id": ctx.forward_from.photo.big_file_id,
                "big_photo_unique_id": (
                    ctx.forward_from.photo.big_photo_unique_id
                ),
            }

        return ""

    if ctx.from_user and ctx.from_user.photo:
        return {
            "small_file_id": ctx.from_user.photo.small_file_id,
            "small_photo_unique_id": ctx.from_user.photo.small_photo_unique_id,
            "big_file_id": ctx.from_user.photo.big_file_id,
            "big_photo_unique_id": ctx.from_user.photo.big_photo_unique_id,
        }

    if (
        ctx.from_user
        or (ctx.sender_chat and not ctx.sender_chat.photo)
        or not ctx.sender_chat
    ):
        return ""

    if ctx.sender_chat.photo:
        return {
            "small_file_id": ctx.sender_chat.photo.small_file_id,
            "small_photo_unique_id": (
                ctx.sender_chat.photo.small_photo_unique_id
            ),
            "big_file_id": ctx.sender_chat.photo.big_file_id,
            "big_photo_unique_id": (
                ctx.sender_chat.photo.big_photo_unique_id
            ),
        }

    return ""


async def get_text_or_caption(ctx: Message):
    if ctx.text:
        return ctx.text

    if ctx.caption:
        return ctx.caption

    return ""


async def pyrogram_to_quotly(messages, is_reply=False):
    if not isinstance(messages, list):
        messages = [messages]

    payload = {
        "type": "quote",
        "format": "png",
        "backgroundColor": "#1b1429",
        "messages": [],
    }

    for message in messages:
        message_data = {}

        if message.entities:
            message_data["entities"] = [
                {
                    "type": entity.type.name.lower(),
                    "offset": entity.offset,
                    "length": entity.length,
                }
                for entity in message.entities
            ]

        elif message.caption_entities:
            message_data["entities"] = [
                {
                    "type": entity.type.name.lower(),
                    "offset": entity.offset,
                    "length": entity.length,
                }
                for entity in message.caption_entities
            ]

        else:
            message_data["entities"] = []

        sender_id = await get_message_sender_id(message)

        message_data["chatId"] = sender_id
        message_data["text"] = await get_text_or_caption(message)
        message_data["avatar"] = True

        message_data["from"] = {
            "id": sender_id,
            "name": await get_message_sender_name(message),
            "username": await get_message_sender_username(message),
            "type": message.chat.type.name.lower(),
            "photo": await get_message_sender_photo(message),
        }

        if message.reply_to_message and is_reply:
            message_data["replyMessage"] = {
                "name": await get_message_sender_name(
                    message.reply_to_message
                ),
                "text": await get_text_or_caption(
                    message.reply_to_message
                ),
                "chatId": await get_message_sender_id(
                    message.reply_to_message
                ),
            }
        else:
            message_data["replyMessage"] = {}

        payload["messages"].append(message_data)

    endpoints = [
        "https://quote.yuri.ly/generate.png",
        "https://quotly.ziash.me/generate",
        "https://bot.lyo.su/quote/generate.png",
    ]

    for url in endpoints:
        try:
            response = await fetch.post(url, json=payload)

            if response.status_code == 200:
                return response.read()

        except Exception:
            continue

    raise QuotlyException(
        "ᴜɴᴀʙʟᴇ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ǫᴜᴏᴛᴇ ʀɪɢʜᴛ ɴᴏᴡ."
    )


def isArgInt(txt) -> list:
    try:
        return [True, int(txt)]
    except (ValueError, TypeError):
        return [False, 0]


@app.on_message(filters.command(["q", "rq"]) & filters.reply)
async def alisa_quotly(client: Client, ctx: Message):

    command = ctx.command[0].lower()
    is_reply = command == "rq"

    loading = await ctx.reply_text(
        "<blockquote>"
        "🌸 <b>𝐀ʟɪsᴀ ǫᴜᴏᴛᴇ</b>\n"
        "⏳ <b>ɢᴇɴᴇʀᴀᴛɪɴɢ ǫᴜᴏᴛᴇ...</b>"
        "</blockquote>"
    )

    # Multiple messages
    if len(ctx.command) > 1:

        check_arg = isArgInt(ctx.command[1])

        if not check_arg[0]:
            return await loading.edit_text(
                "<blockquote>"
                "❌ <b>ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.</b>\n"
                "➜ ᴜsᴇ: <code>/q 5</code>"
                "</blockquote>"
            )

        count = check_arg[1]

        if count < 2 or count > 10:
            return await loading.edit_text(
                "<blockquote>"
                "❌ <b>ɪɴᴠᴀʟɪᴅ ʀᴀɴɢᴇ.</b>\n"
                "➜ ᴄʜᴏᴏsᴇ ᴀ ɴᴜᴍʙᴇʀ ʙᴇᴛᴡᴇᴇɴ "
                "<b>2</b> ᴀɴᴅ <b>10</b>."
                "</blockquote>"
            )

        try:
            messages = [
                msg
                for msg in await client.get_messages(
                    chat_id=ctx.chat.id,
                    message_ids=range(
                        ctx.reply_to_message.id,
                        ctx.reply_to_message.id + count,
                    ),
                    replies=-1,
                )
                if not msg.empty and not msg.media
            ]

        except Exception:
            return await loading.edit_text(
                "<blockquote>"
                "❌ <b>ᴍᴇssᴀɢᴇ ᴇxᴛʀᴀᴄᴛɪᴏɴ ғᴀɪʟᴇᴅ.</b>"
                "</blockquote>"
            )

        if not messages:
            return await loading.edit_text(
                "<blockquote>"
                "❌ <b>ɴᴏ ᴠᴀʟɪᴅ ᴍᴇssᴀɢᴇs ғᴏᴜɴᴅ.</b>"
                "</blockquote>"
            )

        try:
            await loading.edit_text(
                "<blockquote>"
                "🌸 <b>𝐀ʟɪsᴀ ǫᴜᴏᴛᴇ</b>\n"
                "✨ <b>ɢᴇɴᴇʀᴀᴛɪɴɢ sᴛɪᴄᴋᴇʀ...</b>"
                "</blockquote>"
            )

            quote = await pyrogram_to_quotly(
                messages,
                is_reply=is_reply,
            )

            sticker = BytesIO(quote)
            sticker.name = "alisa_quote.webp"

            await ctx.reply_sticker(sticker)
            await loading.delete()

        except Exception as e:
            return await loading.edit_text(
                f"<blockquote>"
                f"❌ <b>ǫᴜᴏᴛᴇ ᴇʀʀᴏʀ</b>\n"
                f"<code>{e}</code>"
                f"</blockquote>"
            )

        return

    # Single message
    try:
        message = await client.get_messages(
            chat_id=ctx.chat.id,
            message_ids=ctx.reply_to_message.id,
            replies=-1,
        )

        messages = [message]

    except Exception:
        return await loading.edit_text(
            "<blockquote>"
            "❌ <b>ᴍᴇssᴀɢᴇ ᴇxᴛʀᴀᴄᴛɪᴏɴ ғᴀɪʟᴇᴅ.</b>"
            "</blockquote>"
        )

    try:
        await loading.edit_text(
            "<blockquote>"
            "🌸 <b>𝐀ʟɪsᴀ ǫᴜᴏᴛᴇ</b>\n"
            "✨ <b>ᴍᴀᴋɪɴɢ ʏᴏᴜʀ sᴛɪᴄᴋᴇʀ...</b>"
            "</blockquote>"
        )

        quote = await pyrogram_to_quotly(
            messages,
            is_reply=is_reply,
        )

        sticker = BytesIO(quote)
        sticker.name = "alisa_quote.webp"

        await ctx.reply_sticker(sticker)
        await loading.delete()

    except Exception as e:
        return await loading.edit_text(
            f"<blockquote>"
            f"❌ <b>ǫᴜᴏᴛᴇ ᴇʀʀᴏʀ</b>\n"
            f"<code>{e}</code>"
            f"</blockquote>"
                )
