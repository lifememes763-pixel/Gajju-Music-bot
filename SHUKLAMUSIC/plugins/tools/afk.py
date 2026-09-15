import time

from pyrogram import filters
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message

from SHUKLAMUSIC import app
from SHUKLAMUSIC.mongo.readable_time import get_readable_time
from SHUKLAMUSIC.mongo.afkdb import add_afk, is_afk, remove_afk


@app.on_message(
    filters.command(
        ["fk", "afk", "off", "bye", "ye"],
        prefixes=["a", "A", "b", "B", "/", "!", "."],
    )
)
async def active_afk(_, message: Message):
    if message.sender_chat or not message.from_user:
        return

    user_id = message.from_user.id

    reason = None
    if len(message.command) > 1:
        reason = message.text.split(None, 1)[1].strip()[:100]

    afk_data = {
        "type": "text_reason" if reason else "text",
        "time": time.time(),
        "data": None,
        "reason": reason,
    }

    await add_afk(user_id, afk_data)

    text = f"❖ {message.from_user.first_name} ɪs ɴᴏᴡ ᴀғᴋ!"

    if reason:
        text += f"\n\n● ʀᴇᴀsᴏɴ: `{reason}`"

    await message.reply_text(text)


@app.on_message(
    ~filters.me & ~filters.bot & ~filters.via_bot,
    group=1,
)
async def chat_watcher_func(_, message: Message):
    if message.sender_chat or not message.from_user:
        return

    if message.text:
        lowered = message.text.lower()

        if any(
            lowered.startswith(prefix + cmd)
            for prefix in ["/", ".", "!", "a", "b"]
            for cmd in ["afk", "fk", "off", "bye", "ye"]
        ):
            return

    msg = ""

    user_id = message.from_user.id
    user_name = message.from_user.first_name

    verifier, afk_data = await is_afk(user_id)

    if verifier:
        await remove_afk(user_id)

        seenago = get_readable_time(
            int(time.time() - afk_data["time"])
        )

        reason = afk_data.get("reason")

        if afk_data.get("type") == "text_reason" and reason:
            msg += (
                f"<b>❖ {user_name[:25]}</b> ɪs ʙᴀᴄᴋ ᴀғᴛᴇʀ {seenago}\n\n"
                f"● ʀᴇᴀsᴏɴ: `{reason}`\n\n"
            )
        else:
            msg += (
                f"<b>❖ {user_name[:25]}</b> ɪs ʙᴀᴄᴋ ᴀғᴛᴇʀ {seenago}\n\n"
            )

    if message.reply_to_message:
        try:
            replied_user = message.reply_to_message.from_user

            if replied_user:
                afk_check, afk_data = await is_afk(
                    replied_user.id
                )

                if afk_check:
                    seenago = get_readable_time(
                        int(time.time() - afk_data["time"])
                    )

                    reason = afk_data.get("reason")

                    if (
                        afk_data.get("type") == "text_reason"
                        and reason
                    ):
                        msg += (
                            f"<b>❖ {replied_user.first_name[:25]}</b> "
                            f"ɪs ᴀғᴋ ғᴏʀ {seenago}\n\n"
                            f"● ʀᴇᴀsᴏɴ: `{reason}`\n\n"
                        )
                    else:
                        msg += (
                            f"<b>❖ {replied_user.first_name[:25]}</b> "
                            f"ɪs ᴀғᴋ ғᴏʀ {seenago}\n\n"
                        )
        except Exception:
            pass

    if message.entities and message.text:
        for ent in message.entities:
            try:
                if ent.type == MessageEntityType.MENTION:
                    username = message.text[
                        ent.offset + 1 : ent.offset + ent.length
                    ]
                    user = await app.get_users(username)

                elif ent.type == MessageEntityType.TEXT_MENTION:
                    user = ent.user

                else:
                    continue

                if not user:
                    continue

                afk_check, afk_data = await is_afk(user.id)

                if afk_check:
                    seenago = get_readable_time(
                        int(time.time() - afk_data["time"])
                    )

                    reason = afk_data.get("reason")

                    if (
                        afk_data.get("type") == "text_reason"
                        and reason
                    ):
                        msg += (
                            f"<b>❖ {user.first_name[:25]}</b> "
                            f"ɪs ᴀғᴋ ғᴏʀ {seenago}\n\n"
                            f"● ʀᴇᴀsᴏɴ: `{reason}`\n\n"
                        )
                    else:
                        msg += (
                            f"<b>❖ {user.first_name[:25]}</b> "
                            f"ɪs ᴀғᴋ ғᴏʀ {seenago}\n\n"
                        )

            except Exception:
                continue

    if msg:
        await message.reply_text(msg)
