from pyrogram import filters
from pyrogram.types import Message
from SHUKLAMUSIC import app
from config import OWNER_ID
import aiohttp
import re
from telethon import Button


# ───────── VC START ─────────

@app.on_message(filters.video_chat_started)
async def vc_started(_, message):
    await message.reply_text("🎙️ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ɪs ʟɪᴠᴇ")


# ───────── VC END ─────────

@app.on_message(filters.video_chat_ended)
async def vc_ended(_, message):
    await message.reply_text("🔕 ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴄʟᴏsᴇᴅ")


# ───────── VC INVITE ─────────

@app.on_message(filters.video_chat_members_invited)
async def vc_invited(_, message: Message):
    invited = message.video_chat_members_invited.users

    names = []
    for user in invited:
        try:
            names.append(f"[{user.first_name}](tg://user?id={user.id})")
        except Exception:
            continue

    if names:
        text = f"📢 {message.from_user.mention} ɪɴᴠɪᴛᴇᴅ " + " ".join(names)
        await message.reply_text(text)


# ───────── MATH ─────────

@app.on_message(filters.command("math"))
async def calculate_math(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "❌ ᴜsᴀɢᴇ: `/math 2+2`",
            quote=True
        )

    expression = message.text.split(None, 1)[1]

    try:
        result = eval(expression)
        response = f"🧮 **Answer:** `{result}`"
    except Exception:
        response = "❌ ɪɴᴠᴀʟɪᴅ ᴇxᴘʀᴇssɪᴏɴ"

    await message.reply_text(response, quote=True)


# ───────── LEAVE GROUP ─────────

@app.on_message(filters.command("leavegroup") & filters.user(OWNER_ID))
async def bot_leave(_, message):
    await message.reply_text("👋 ʟᴇᴀᴠɪɴɢ ᴛʜɪs ᴄʜᴀᴛ...")
    await app.leave_chat(message.chat.id)


# ───────── GOOGLE SEARCH ─────────

@app.on_message(filters.command("spg", prefixes=["/", "!", "."]))
async def search(event):
    if len(event.text.split()) < 2:
        return await event.reply("❌ ɢɪᴠᴇ ᴀ sᴇᴀʀᴄ ᴛᴇʀᴍ")

    query = event.text.split(None, 1)[1]
    msg = await event.respond("🔎 sᴇᴀʀᴄɪɴɢ...")

    async with aiohttp.ClientSession() as session:
        url = "https://content-customsearch.googleapis.com/customsearch/v1"

        params = {
            "cx": "ec8db9e1f9e41e65e",
            "q": query,
            "key": config.GOOGLE_API_KEY,
            "start": 1
        }

        async with session.get(
            url,
            params=params,
            headers={
                "x-referer": "https://explorer.apis.google.com"
            }
        ) as r:
            response = await r.json()

    items = response.get("items", [])

    if not items:
        return await msg.edit("🔍 ɴᴏ ʀᴇsᴜʟᴛs")

    result = ""
    seen = set()

    for item in items:
        title = item.get("title", "Untitled")
        link = item.get("link")

        if not link or link in seen:
            continue

        seen.add(link)

        if "?" in link:
            link = link.split("?")[0]

        result += f"**{title}**\n{link}\n\n"

    await msg.edit(
        result or "🔍 ɴᴏ ʀᴇsᴜʟᴛs",
        link_preview=False
    )
