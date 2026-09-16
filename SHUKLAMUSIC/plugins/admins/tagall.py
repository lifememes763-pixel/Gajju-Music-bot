# ---------------------------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla
# 📅 Copyright © 2025 – All Rights Reerved
# ---------------------------------------------------------------

import asyncio
import random
import re

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ParseMode
from pyrogram.errors import FloodWait

from SHUKLAMUSIC import app


SPAM_CHATS = []

EMOJI = [
    "🦋🦋🦋🦋🦋",
    "🧚🌸🧋🍬🫖",
    "🥀🌷🌹🌺💐",
    "🌸🌿💮🌱🌵",
    "❤️💚💙💜🖤",
    "💓💕💞💗💖",
    "🌸💐🌺🌹🦋",
    "🍔🦪🍛🍲🥗",
    "🍎🍓🍒🍑🌶️",
    "🧋🥤🧋🥛🍷",
    "🍬🍭🧁🎂🍡",
    "🍨🧉🍺☕🍻",
    "🥪🥧🍦🍥🍚",
    "🫖☕🍹🍷🥛",
    "☕🧃🍩🍦🍙",
    "🍁🌾💮🍂🌿",
    "🌨️🌥️⛈️🌩️🌧️",
    "🌷🏵️🌸🌺💐",
    "💮🌼🌻🍀🍁",
    "🧟🦸🦹🧙👸",
    "🧅🍠🥕🌽🥦",
    "🐷🐹🐭🐨🐻‍❄️",
    "🦋🐇🐀🐈🐈‍⬛",
    "🌼🌳🌲🌴🌵",
    "🥩🍋🍐🍈🍇",
    "🍴🍽️🔪🍶🥃",
    "🕌🏰🏩⛩️🏩",
    "🎉🎊🎈🎂🎀",
    "🪴🌵🌴🌳🌲",
    "🎄🎋🎍🎑🎎",
    "🦅🦜🕊️🦤🦢",
    "🦤🦩🦚🦃🦆",
    "🐬🦭🦈🐋🐳",
    "🐔🐟🐠🐡🦐",
    "🦩🦀🦑🐙🦪",
    "🐦🦂🕷️🕸️🐚",
    "🥪🍰🥧🍨🍨",
    "🥬🍉🧁🧇🔮",
]


def clean_text(text):
    if not text:
        return ""
    return re.sub(r"([_*[\]()~`>#+-=|{}.!])", r"\\\1", text)


async def is_admin(chat_id, user_id):
    admin_ids = [
        admin.user.id
        async for admin in app.get_chat_members(
            chat_id,
            filter=ChatMembersFilter.ADMINISTRATORS,
        )
    ]
    return user_id in admin_ids


async def process_members(chat_id, members, text=None, replied=None):
    tagged_members = 0
    usernum = 0
    usertxt = ""

    emoji_sequence = random.choice(EMOJI)
    emoji_index = 0

    for member in members:
        if chat_id not in SPAM_CHATS:
            break

        if member.user.is_deleted or member.user.is_bot:
            continue

        tagged_members += 1
        usernum += 1

        emoji = emoji_sequence[emoji_index % len(emoji_sequence)]
        usertxt += f"[{emoji}](tg://user?id={member.user.id}) "
        emoji_index += 1

        if usernum == 5:
            try:
                if replied:
                    await replied.reply_text(
                        usertxt,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                else:
                    await app.send_message(
                        chat_id,
                        f"{text}\n{usertxt}",
                        parse_mode=ParseMode.MARKDOWN,
                    )

                await asyncio.sleep(2)

                usernum = 0
                usertxt = ""
                emoji_sequence = random.choice(EMOJI)
                emoji_index = 0

            except FloodWait as e:
                await asyncio.sleep(e.value + 2)

            except Exception as e:
                await app.send_message(
                    chat_id,
                    f"Error while tagging: {str(e)}",
                )
                continue

    if usernum > 0 and chat_id in SPAM_CHATS:
        try:
            if replied:
                await replied.reply_text(
                    usertxt,
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                await app.send_message(
                    chat_id,
                    f"{text}\n\n{usertxt}",
                    parse_mode=ParseMode.MARKDOWN,
                )

        except Exception as e:
            await app.send_message(
                chat_id,
                f"Error sending final batch: {str(e)}",
            )

    return tagged_members


@app.on_message(
    filters.command(
        ["all", "allmention", "mentionall", "tagall"],
        prefixes=["/", "@"],
    )
)
async def tag_all_users(_, message):

    if not message.from_user:
        return

    admin = await is_admin(
        message.chat.id,
        message.from_user.id,
    )

    if not admin:
        return await message.reply_text(
            "Only admins can use this command."
        )

    if message.chat.id in SPAM_CHATS:
        return await message.reply_text(
            "Tagging process is already running. Use /cancel to stop it."
        )

    replied = message.reply_to_message

    if len(message.command) < 2 and not replied:
        return await message.reply_text(
            "Give some text to tag all, like: `@all Hi Friends`"
        )

    try:
        members = []

        async for m in app.get_chat_members(
            message.chat.id
        ):
            members.append(m)

        total_members = len(members)

        SPAM_CHATS.append(message.chat.id)

        text = None

        if not replied:
            text = clean_text(
                message.text.split(None, 1)[1]
            )

        tagged_members = await process_members(
            message.chat.id,
            members,
            text=text,
            replied=replied,
        )

        summary_msg = (
            "✅ Tagging completed!\n\n"
            f"Total members: {total_members}\n"
            f"Tagged members: {tagged_members}"
        )

        await app.send_message(
            message.chat.id,
            summary_msg,
        )

    except FloodWait as e:
        await asyncio.sleep(e.value)

    except Exception as e:
        await app.send_message(
            message.chat.id,
            f"An error occurred: {str(e)}",
        )

    finally:
        try:
            SPAM_CHATS.remove(message.chat.id)
        except Exception:
            pass


@app.on_message(
    filters.command(
        ["admintag", "adminmention", "admins", "report"],
        prefixes=["/", "@"],
    )
)
async def tag_all_admins(_, message):

    if not message.from_user:
        return

    admin = await is_admin(
        message.chat.id,
        message.from_user.id,
    )

    if not admin:
        return await message.reply_text(
            "Only admins can use this command."
        )

    if message.chat.id in SPAM_CHATS:
        return await message.reply_text(
            "Tagging process is already running. Use /cancel to stop it."
        )

    replied = message.reply_to_message

    if len(message.command) < 2 and not replied:
        return await message.reply_text(
            "Give some text to tag admins, like: `@admins Hi Friends`"
        )

    try:
        members = []

        async for m in app.get_chat_members(
            message.chat.id,
            filter=ChatMembersFilter.ADMINISTRATORS,
        ):
            members.append(m)

        total_admins = len(members)

        SPAM_CHATS.append(message.chat.id)

        text = None

        if not replied:
            text = clean_text(
                message.text.split(None, 1)[1]
            )

        tagged_admins = await process_members(
            message.chat.id,
            members,
            text=text,
            replied=replied,
        )

        summary_msg = (
            "✅ Admin tagging completed!\n\n"
            f"Total admins: {total_admins}\n"
            f"Tagged admins: {tagged_admins}"
        )

        await app.send_message(
            message.chat.id,
            summary_msg,
        )

    except FloodWait as e:
        await asyncio.sleep(e.value)

    except Exception as e:
        await app.send_message(
            message.chat.id,
            f"An error occurred: {str(e)}",
        )

    finally:
        try:
            SPAM_CHATS.remove(message.chat.id)
        except Exception:
            pass


@app.on_message(
    filters.command(
        [
            "stopmention",
            "cancel",
            "cancelmention",
            "offmention",
            "mentionoff",
            "cancelall",
        ],
        prefixes=["/", "@"],
    )
)
async def cancelcmd(_, message):

    if not message.from_user:
        return

    chat_id = message.chat.id

    admin = await is_admin(
        chat_id,
        message.from_user.id,
    )

    if not admin:
        return await message.reply_text(
            "Only admins can use this command."
        )

    if chat_id in SPAM_CHATS:
        try:
            SPAM_CHATS.remove(chat_id)
        except Exception:
            pass

        return await message.reply_text(
            "Tagging process successfully stopped!"
        )

    return await message.reply_text(
        "No tagging process is currently running!"
                    )
