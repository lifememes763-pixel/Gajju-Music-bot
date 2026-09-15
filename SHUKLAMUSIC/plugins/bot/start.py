import asyncio
import random
import time
import yt_dlp

from pyrogram import filters
from pyrogram.enums import ChatType, ButtonStyle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import _boot_
from SHUKLAMUSIC.plugins.sudo.sudoers import sudoers_list
from SHUKLAMUSIC.utils import bot_sys_stats
from SHUKLAMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    get_served_chats,
    get_served_users,
    is_banned_user,
)
from SHUKLAMUSIC.utils.decorators.language import LanguageStart
from SHUKLAMUSIC.utils.formatters import get_readable_time
from SHUKLAMUSIC.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string


try:
    from SHUKLAMUSIC.core.mongo import mongodb as db
except ImportError:
    from SHUKLAMUSIC.utils.database import mongodb as db


welcome_db = db.welcome_config

YUMI_PICS = [
    "https://i.ibb.co/bgzQ2YV1/v-Y9z-JCSF.jpg",
    "https://i.ibb.co/yFHCgpRG/p5-Vg-N6-Au.jpg",
    "https://i.ibb.co/bRFNr2Qy/g-Ps-ZKm-Ma.jpg",
]

GREET = ["💞", "🥂", "🔍", "🧪", "⚡", "🔥"]


async def send_reaction(client, message, emoji="💖"):
    try:
        await message.react(emoji=emoji)
        return
    except Exception:
        pass

    try:
        await client.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji=emoji,
        )
    except Exception:
        pass


async def get_welcome_caption(msg_type, default_text, user, bot, chat=None):
    data = await welcome_db.find_one({"_id": msg_type})

    if not data or "message" not in data:
        return default_text

    text = data["message"]

    first_name = getattr(user, "first_name", "User")
    mention = getattr(user, "mention", first_name)
    username = getattr(user, "username", None)
    bot_name = getattr(bot, "first_name", "Music Bot")

    text = text.replace("{name}", first_name)
    text = text.replace("{mention}", mention)
    text = text.replace(
        "{username}",
        f"@{username}" if username else "No Username",
    )
    text = text.replace("{bot_name}", bot_name)

    if chat:
        text = text.replace(
            "{chat_name}",
            getattr(chat, "title", "Group"),
        )

    return text


# ================================
#       SET WELCOME COMMANDS
# ================================

@app.on_message(
    filters.command(["setwelcome_dm", "setwelcome_grp"])
    & filters.user(8915827098)
)
async def set_welcome_msg(client, message):
    cmd = message.command[0].lower()
    msg_type = "welcome_dm" if "dm" in cmd else "welcome_group"

    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text(
            f"❌ <b>Usage:</b>\n"
            f"<code>/{cmd} Your HTML Message</code>\n\n"
            "<b>Variables:</b>\n"
            "<code>{name}</code> - First Name\n"
            "<code>{mention}</code> - User Mention\n"
            "<code>{username}</code> - Username\n"
            "<code>{bot_name}</code> - Bot Name\n"
            "<code>{chat_name}</code> - Group Name"
        )
        return

    try:
        if message.reply_to_message:
            replied = message.reply_to_message

            if replied.text:
                new_msg = replied.text.html
            elif replied.caption:
                new_msg = replied.caption.html
            else:
                raise AttributeError
        else:
            new_msg = message.text.html.split(None, 1)[1]

    except (IndexError, AttributeError):
        await message.reply_text(
            "❌ Message text extract nahi ho paya."
        )
        return

    await welcome_db.update_one(
        {"_id": msg_type},
        {"$set": {"message": new_msg}},
        upsert=True,
    )

    await message.reply_text(
        f"✅ <b>{msg_type.replace('_', ' ').upper()} message saved!</b>"
    )


@app.on_message(
    filters.command(["resetwelcome"])
    & filters.user(8915827098)
)
async def reset_welcome_msg(client, message):
    msg_type = "welcome_dm"

    if len(message.command) > 1:
        if message.command[1].lower() in ("grp", "group"):
            msg_type = "welcome_group"

    result = await welcome_db.delete_one(
        {"_id": msg_type}
    )

    if result.deleted_count:
        await message.reply_text(
            f"✅ <b>{msg_type.replace('_', ' ').upper()} reset!</b>\n"
            "Default welcome message active hai."
        )
    else:
        await message.reply_text(
            f"ℹ️ <b>{msg_type.replace('_', ' ')} saved nahi tha.</b>"
        )


# ================================
#          START - PRIVATE
# ================================

@app.on_message(
    filters.command(["start"])
    & filters.private
    & ~BANNED_USERS
)
@LanguageStart
async def start_pm(client, message: Message, _):
    await send_reaction(client, message, "💖")

    await add_served_user(message.from_user.id)

    try:
        greet_msg = await message.reply_text(
            random.choice(GREET)
        )
        await asyncio.sleep(0.3)
        await greet_msg.delete()
    except Exception:
        pass

    if len(message.command) > 1:
        name = message.command[1]

        # ---------- HELP ----------
        if name.startswith("help"):
            keyboard = help_pannel(_)

            await message.reply_photo(
                photo=random.choice(YUMI_PICS),
                has_spoiler=True,
                caption=_["help_1"].format(
                    config.SUPPORT_CHAT
                ),
                reply_markup=keyboard,
            )
            return

        # ---------- SUDO ----------
        if name.startswith("sud"):
            await sudoers_list(
                client=client,
                message=message,
                _=_,
            )
            return

        # ---------- VIDEO INFO ----------
        if name.startswith("inf"):
            status = await message.reply_text("🔎")

            video_id = name.replace(
                "info_",
                "",
                1,
            )

            video_url = (
                f"https://www.youtube.com/watch?v={video_id}"
            )

            def fetch_yt_info():
                options = {
                    "quiet": True,
                    "no_warnings": True,
                    "skip_download": True,
                    "noplaylist": True,
                    "extract_flat": False,
                }

                with yt_dlp.YoutubeDL(options) as ydl:
                    return ydl.extract_info(
                        video_url,
                        download=False,
                    ) or {}

            try:
                loop = asyncio.get_running_loop()

                info = await loop.run_in_executor(
                    None,
                    fetch_yt_info,
                )

            except Exception:
                await status.edit_text(
                    "❌ <b>YouTube information fetch nahi ho payi.</b>\n"
                    "Video private, deleted ya unavailable ho sakta hai."
                )
                return

            title = info.get(
                "title"
            ) or "Unknown Title"

            duration_seconds = int(
                info.get("duration") or 0
            )

            hours, remainder = divmod(
                duration_seconds,
                3600,
            )

            minutes, seconds = divmod(
                remainder,
                60,
            )

            if hours:
                duration = (
                    f"{hours}:{minutes:02d}:{seconds:02d}"
                )
            else:
                duration = (
                    f"{minutes}:{seconds:02d}"
                )

            views_count = int(
                info.get("view_count") or 0
            )

            if views_count >= 1_000_000_000:
                views = (
                    f"{views_count / 1_000_000_000:.1f}B views"
                )
            elif views_count >= 1_000_000:
                views = (
                    f"{views_count / 1_000_000:.1f}M views"
                )
            elif views_count >= 1_000:
                views = (
                    f"{views_count / 1_000:.1f}K views"
                )
            else:
                views = (
                    f"{views_count} views"
                    if views_count
                    else "Unknown Views"
                )

            thumbnail = info.get("thumbnail")

            channel_link = (
                info.get("channel_url")
                or info.get("uploader_url")
                or ""
            )

            channel_name = (
                info.get("uploader")
                or info.get("channel")
                or "Unknown"
            )

            upload_date = (
                info.get("upload_date") or ""
            )

            months = [
                "Jan", "Feb", "Mar", "Apr",
                "May", "Jun", "Jul", "Aug",
                "Sep", "Oct", "Nov", "Dec",
            ]

            if len(upload_date) == 8:
                try:
                    published = (
                        f"{upload_date[6:]} "
                        f"{months[int(upload_date[4:6]) - 1]} "
                        f"{upload_date[:4]}"
                    )
                except Exception:
                    published = "Unknown"
            else:
                published = "Unknown"

            searched_text = _["start_6"].format(
                title,
                duration,
                views,
                published,
                channel_link,
                channel_name,
                app.mention,
            )

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=_["S_B_8"],
                            url=video_url,
                            style=ButtonStyle.PRIMARY,
                        ),
                        InlineKeyboardButton(
                            text=_["S_B_9"],
                            url=config.SUPPORT_CHAT,
                            style=ButtonStyle.DANGER,
                        ),
                    ]
                ]
            )

            try:
                await status.delete()

                if thumbnail:
                    await app.send_photo(
                        chat_id=message.chat.id,
                        photo=thumbnail,
                        caption=searched_text,
                        reply_markup=keyboard,
                    )
                else:
                    await app.send_message(
                        chat_id=message.chat.id,
                        text=searched_text,
                        reply_markup=keyboard,
                    )

            except Exception:
                await message.reply_text(
                    "❌ Video information send nahi ho payi."
                )

            return

    # ---------- NORMAL START ----------

    out = private_panel(_)

    served_chats = len(
        await get_served_chats()
    )

    served_users = len(
        await get_served_users()
    )

    UP, CPU, RAM, DISK = await bot_sys_stats()

    default_caption = _["start_2"].format(
        message.from_user.mention,
        app.mention,
        UP,
        DISK,
        CPU,
        RAM,
        served_users,
        served_chats,
    )

    me = await client.get_me()

    final_caption = await get_welcome_caption(
        "welcome_dm",
        default_caption,
        message.from_user,
        me,
    )

    await message.reply_photo(
        photo=random.choice(YUMI_PICS),
        has_spoiler=True,
        caption=final_caption,
        reply_markup=InlineKeyboardMarkup(out),
    )

    # ---------- PRIVATE LOGGER ----------

    user = message.from_user

    username = (
        f"@{user.username}"
        if user.username
        else "ɴᴏɴᴇ"
    )

    log_text = (
        "<blockquote>"
        "📝 <b>ᴍᴜsɪᴄ ʙᴏᴛ sᴛᴀʀᴛᴇᴅ ɪɴ ᴘʀɪᴠᴀᴛᴇ</b>\n\n"
        f"👤 <b>ᴜsᴇʀ:</b> {user.mention}\n"
        f"🍂 <b>ɪᴅ:</b> <code>{user.id}</code>\n"
        f"🔐 <b>ᴜsᴇʀɴᴀᴍᴇ:</b> {username}"
        "</blockquote>"
    )

    if getattr(config, "LOGGER_ID", None):
        try:
            await app.send_message(
                config.LOGGER_ID,
                log_text,
            )
        except Exception as error:
            print(
                f"Logger error: {error}"
            )

    if getattr(config, "OWNER_ID", None):
        try:
            owners = (
                config.OWNER_ID
                if isinstance(config.OWNER_ID, list)
                else [config.OWNER_ID]
            )

            for owner_id in owners:
                await app.send_message(
                    int(owner_id),
                    log_text,
                )

        except Exception as error:
            print(
                f"Owner logger error: {error}"
            )


# ================================
#          START - GROUP
# ================================

@app.on_message(
    filters.command(["start"])
    & filters.group
    & ~BANNED_USERS
)
@LanguageStart
async def start_gp(client, message: Message, _):
    await send_reaction(
        client,
        message,
        "🥰",
    )

    out = start_panel(_)

    uptime = int(
        time.time() - _boot_
    )

    default_caption = _["start_1"].format(
        app.mention,
        get_readable_time(uptime),
    )

    final_caption = await get_welcome_caption(
        "welcome_group",
        default_caption,
        message.from_user,
        await client.get_me(),
        message.chat,
    )

    await message.reply_photo(
        photo=random.choice(YUMI_PICS),
        caption=final_caption,
        reply_markup=InlineKeyboardMarkup(out),
    )

    await add_served_chat(
        message.chat.id
    )


# ================================
#         NEW MEMBER WELCOME
# ================================

@app.on_message(
    filters.new_chat_members,
    group=-1,
)
async def welcome(client, message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(
                message.chat.id
            )

            _ = get_string(language)

            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(
                        member.id
                    )
                except Exception:
                    pass

            if member.id != app.id:
                continue

            if message.chat.type != ChatType.SUPERGROUP:
                await message.reply_text(
                    _["start_4"]
                )

                await app.leave_chat(
                    message.chat.id
                )
                return

            if message.chat.id in await blacklisted_chats():
                await message.reply_text(
                    _["start_5"].format(
                        app.mention,
                        f"https://t.me/{app.username}?start=sudolist",
                        config.SUPPORT_CHAT,
                    ),
                    disable_web_page_preview=True,
                )

                await app.leave_chat(
                    message.chat.id
                )
                return

            out = start_panel(_)

            default_caption = _["start_3"].format(
                message.from_user.mention
                if message.from_user
                else "Unknown",
                app.mention,
                message.chat.title,
                app.mention,
            )

            final_caption = await get_welcome_caption(
                "welcome_group",
                default_caption,
                member,
                await client.get_me(),
                message.chat,
            )

            await message.reply_photo(
                photo=random.choice(YUMI_PICS),
                has_spoiler=True,
                caption=final_caption,
                reply_markup=InlineKeyboardMarkup(out),
            )

            await add_served_chat(
                message.chat.id
            )

            await message.stop_propagation()

        except Exception as error:
            print(
                f"Welcome error: {error}"
                )
