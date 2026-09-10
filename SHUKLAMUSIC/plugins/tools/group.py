# -----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Voice Chat + Utility Commands
# -----------------------------------------------

import ast
import operator
import aiohttp

from pyrogram import filters
from pyrogram.types import Message

from SHUKLAMUSIC import app
from config import OWNER_ID, GOOGLE_API_KEY


# ───────── SAFE MATH ─────────

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_math(expression):
    """Safely calculate basic arithmetic without eval()."""

    if len(expression) > 100:
        raise ValueError

    tree = ast.parse(expression, mode="eval")

    def calculate(node):

        if isinstance(node, ast.Expression):
            return calculate(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                if isinstance(node.value, bool):
                    raise ValueError
                return node.value
            raise ValueError

        if isinstance(node, ast.UnaryOp):
            operation = _ALLOWED_OPERATORS.get(type(node.op))

            if operation is None:
                raise ValueError

            return operation(calculate(node.operand))

        if isinstance(node, ast.BinOp):
            operation = _ALLOWED_OPERATORS.get(type(node.op))

            if operation is None:
                raise ValueError

            left = calculate(node.left)
            right = calculate(node.right)

            # Prevent huge calculations
            if isinstance(right, (int, float)):
                if abs(right) > 1000000:
                    raise ValueError

            result = operation(left, right)

            if isinstance(result, (int, float)):
                if abs(result) > 10**100:
                    raise ValueError

            return result

        raise ValueError

    return calculate(tree)


# ───────── VC START ─────────

@app.on_message(filters.video_chat_started)
async def vc_started(_, message: Message):
    await message.reply_text(
        "🎙️ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ"
    )


# ───────── VC END ─────────

@app.on_message(filters.video_chat_ended)
async def vc_ended(_, message: Message):
    await message.reply_text(
        "🔕 ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ"
    )


# ───────── VC INVITE ─────────

@app.on_message(filters.video_chat_members_invited)
async def vc_invited(_, message: Message):

    invited = message.video_chat_members_invited.users

    if not invited:
        return

    names = []

    for user in invited:
        try:
            name = user.first_name or "User"
            names.append(
                f"[{name}](tg://user?id={user.id})"
            )
        except Exception:
            continue

    if not names:
        return

    inviter = (
        message.from_user.mention
        if message.from_user
        else "Someone"
    )

    await message.reply_text(
        f"📢 {inviter} ɪɴᴠɪᴛᴇᴅ "
        + " ".join(names)
    )


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
        result = safe_math(expression)

        if isinstance(result, float) and result.is_integer():
            result = int(result)

        response = f"🧮 **Answer:** `{result}`"

    except Exception:
        response = "❌ ɪɴᴠᴀʟɪᴅ ᴇxᴘʀᴇssɪᴏɴ"

    await message.reply_text(
        response,
        quote=True
    )


# ───────── LEAVE GROUP ─────────

@app.on_message(
    filters.command("leavegroup") &
    filters.user(OWNER_ID)
)
async def bot_leave(_, message: Message):

    await message.reply_text(
        "👋 ʟᴇᴀᴠɪɴɢ ᴛʜɪs ᴄʜᴀᴛ..."
    )

    try:
        await app.leave_chat(message.chat.id)
    except Exception:
        await message.reply_text(
            "❌ ᴄᴏᴜʟᴅɴ'ᴛ ʟᴇᴀᴠᴇ ᴛʜɪs ᴄʜᴀᴛ."
        )


# ───────── GOOGLE SEARCH ─────────

@app.on_message(
    filters.command(
        "spg",
        prefixes=["/", "!", "."]
    )
)
async def search(_, message: Message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ ɢɪᴠᴇ ᴀ sᴇᴀʀᴄʜ ᴛᴇʀᴍ."
        )

    if not GOOGLE_API_KEY:
        return await message.reply_text(
            "⚠️ sᴇᴀʀᴄʜ ɪs ᴄᴜʀʀᴇɴᴛʟʏ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ."
        )

    query = message.text.split(None, 1)[1].strip()

    if len(query) > 200:
        return await message.reply_text(
            "❌ sᴇᴀʀᴄʜ ᴛᴇʀᴍ ᴛᴏᴏ ʟᴏɴɢ."
        )

    msg = await message.reply_text(
        "🔎 sᴇᴀʀᴄʜɪɴɢ..."
    )

    url = (
        "https://content-customsearch.googleapis.com/"
        "customsearch/v1"
    )

    params = {
        "cx": "ec8db9e1f9e41e65e",
        "q": query,
        "key": GOOGLE_API_KEY,
        "start": 1
    }

    try:
        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(
                url,
                params=params,
                headers={
                    "x-referer":
                    "https://explorer.apis.google.com"
                }
            ) as response:

                if response.status != 200:
                    return await msg.edit_text(
                        "⚠️ sᴇᴀʀᴄʜ ᴀᴘɪ ᴇʀʀᴏʀ."
                    )

                data = await response.json(
                    content_type=None
                )

    except (aiohttp.ClientError, TimeoutError):
        return await msg.edit_text(
            "⚠️ sᴇᴀʀᴄʜ ᴛɪᴍᴇᴅ ᴏᴜᴛ."
        )

    except Exception:
        return await msg.edit_text(
            "⚠️ sᴇᴀʀᴄʜ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ."
        )

    items = data.get("items", [])

    if not isinstance(items, list) or not items:
        return await msg.edit_text(
            "🔍 ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ."
        )

    result = []
    seen = set()

    for item in items:

        if not isinstance(item, dict):
            continue

        title = item.get("title")
        link = item.get("link")

        if not title or not link:
            continue

        if link in seen:
            continue

        seen.add(link)

        result.append(
            f"**{title}**\n{link}"
        )

    if not result:
        return await msg.edit_text(
            "🔍 ɴᴏ ᴠᴀʟɪᴅ ʀᴇsᴜʟᴛs."
        )

    await msg.edit_text(
        "\n\n".join(result),
        disable_web_page_preview=True
        )
