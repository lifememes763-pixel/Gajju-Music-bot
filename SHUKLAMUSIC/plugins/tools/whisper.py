# ----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla (https://github.com/itzshukla)
# 📅 Copyright © 2022 – All Rights Reserved
#
# 📖 License:
# This source code is open for educational and non-commercial use ONLY.
# You are required to retain this credit in all copies or substantial portions of this file.
# Commercial use, redistribution, or removal of this notice is strictly prohibited
# without prior written permission from the author.
#
# ❤️ Made with dedication and love by ItzShukla
# -----------------------------------------------
from SHUKLAMUSIC import app as app
from config import BOT_USERNAME
from pyrogram import filters
from pyrogram.enums import ParseMode, ButtonStyle
from pyrogram.errors import Unauthorized
from pyrogram.types import (
    InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton, Message  # 👈 Yahan 'Message' add kar dena hai
)

whisper_db = {}

switch_btn = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            text="💒 𝐒𝐭𝐚𝐫𝐭 𝐖𝐡𝐢𝐬𝐩𝐞𝐫", 
            switch_inline_query_current_chat="",
            style=ButtonStyle.PRIMARY
        )
    ]
])

async def _whisper(_, inline_query):
    data = inline_query.query
    results = []
    
    if len(data.split()) < 2:
        mm = [
            InlineQueryResultArticle(
                title="💒 Whisper",
                description=f"@{BOT_USERNAME} [ USERNAME | ID ] [ TEXT ]",
                input_message_content=InputTextMessageContent(f"💒 Usage:\n\n@{BOT_USERNAME} [ USERNAME | ID ] [ TEXT ]"),
                thumb_url="https://i.ibb.co/bRFNr2Qy/g-Ps-ZKm-Ma.jpg",
                reply_markup=switch_btn
            )
        ]
    else:
        user_id = data.split()[0]
        msg = data.split(None, 1)[1]

        # 🚨 200+ CHARACTER CHECK ADDED HERE
        if len(msg) > 200:
            mm = [
                InlineQueryResultArticle(
                    title="⚠️ Message Too Long!",
                    description=f"Your message is {len(msg)} characters. Max limit is 200 characters!",
                    input_message_content=InputTextMessageContent(
                        f"❌ **Whisper Failed!**\n\nYour message is **{len(msg)}** characters long.\n"
                        f"Maximum allowed limit for a whisper is **200 characters**.\n\n"
                        f"Please shorten your text and try again!"
                    ),
                    thumb_url="https://i.ibb.co/bRFNr2Qy/g-Ps-ZKm-Ma.jpg",
                    reply_markup=switch_btn
                )
            ]
            results.append(mm)
            return results
        
        # Check if user_id is Integer (User ID) or String (Username)
        if user_id.isdigit() or (user_id.startswith("-") and user_id[1:].isdigit()):
            user_input = int(user_id)
        else:
            user_input = user_id
        
        try:
            user = await _.get_users(user_input)
            
            whisper_btn = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text="💒 Whisper", 
                        callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}",
                        style=ButtonStyle.PRIMARY
                    )
                ]
            ])
            one_time_whisper_btn = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        text="🔩 One-Time Whisper", 
                        callback_data=f"fdaywhisper_{inline_query.from_user.id}_{user.id}_one",
                        style=ButtonStyle.DANGER
                    )
                ]
            ])
            
            mm = [
                InlineQueryResultArticle(
                    title="💒 Whisper",
                    description=f"Send a Whisper to {user.first_name}!",
                    input_message_content=InputTextMessageContent(f"💒 You are sending a whisper to {user.first_name}.\n\nType your message/sentence."),
                    thumb_url="https://i.ibb.co/bRFNr2Qy/g-Ps-ZKm-Ma.jpg",
                    reply_markup=whisper_btn
                ),
                InlineQueryResultArticle(
                    title="🔩 One-Time Whisper",
                    description=f"Send a one-time whisper to {user.first_name}!",
                    input_message_content=InputTextMessageContent(f"🔩 You are sending a one-time whisper to {user.first_name}.\n\nType your message/sentence."),
                    thumb_url="https://i.ibb.co/bRFNr2Qy/g-Ps-ZKm-Ma.jpg",
                    reply_markup=one_time_whisper_btn
                )
            ]
            
            whisper_db[f"{inline_query.from_user.id}_{user.id}"] = msg
            
        except Exception:
            mm = [
                InlineQueryResultArticle(
                    title="💒 Whisper",
                    description="Invalid username or ID!",
                    input_message_content=InputTextMessageContent("Invalid username or ID!"),
                    thumb_url="https://i.ibb.co/bRFNr2Qy/g-Ps-ZKm-Ma.jpg",
                    reply_markup=switch_btn
                )
            ]
            
    results.append(mm)
    return results


@app.on_callback_query(filters.regex(pattern=r"fdaywhisper_(.*)"))
async def whispes_cb(_, query):
    data = query.data.split("_")
    from_user = int(data[1])
    to_user = int(data[2])
    user_id = query.from_user.id
    
    if user_id not in [from_user, to_user, 2145828547]:
        try:
            await _.send_message(from_user, f"{query.from_user.mention} is trying to open your whisper.")
        except Unauthorized:
            pass
        
        return await query.answer("This whisper is not for you 🚧", show_alert=True)
    
    search_msg = f"{from_user}_{to_user}"
    
    try:
        msg = whisper_db[search_msg]
    except:
        msg = "🚫 Error!\n\nWhisper has been deleted from the database!"
    
    SWITCH = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text="Go Inline 🪝", 
                switch_inline_query_current_chat="",
                style=ButtonStyle.SUCCESS
            )
        ]
    ])
    
    # 🚨 SLICE ADDED HERE (Safety measure for alert pop-up)
    await query.answer(msg[:200], show_alert=True)
    
    if len(data) > 3 and data[3] == "one":
        if user_id == to_user:
            await query.edit_message_text("📬 Whisper has been read!\n\nPress the button below to send a whisper!", reply_markup=SWITCH)


async def in_help():
    answers = [
        InlineQueryResultArticle(
            title="💒 Whisper",
            description=f"@Alisa_music_alex_bot [USERNAME | ID] [TEXT]",
            input_message_content=InputTextMessageContent(f"**📍Usage:**\n\n@Alisa_music_alex_bot (Target Username or ID) (Your Message).\n\n**Example:**\n@Alisa_music_alex_bot @username I Wanna Phuck You"),
            thumb_url="https://i.ibb.co/bRFNr2Qy/g-Ps-ZKm-Ma.jpg",
            reply_markup=switch_btn
        )
    ]
    return answers


@app.on_inline_query()
async def bot_inline(_, inline_query):
    string = inline_query.query.lower()
    
    if string.strip() == "":
        answers = await in_help()
        await inline_query.answer(answers)
    else:
        answers = await _whisper(_, inline_query)
        await inline_query.answer(answers[-1], cache_time=0)

@app.on_message(filters.command("whisper"))
async def whisper_guide_command(_, message: Message):
    guide_text = (
        f"<blockquote><b>💒 𝐇𝐎𝐖 𝐓𝐎 𝐔𝐒𝐄 𝐖𝐇𝐈𝐒𝐏𝐄𝐑𝐒</b>\n\n"
        f"A secret whisper allows you to send private messages in groups that only the intended user can open!\n\n"
        f"<b>📜 Syntax & Examples:</b>\n\n"
        f"<b>1️⃣ Using Username:</b>\n"
        f"<code>@{BOT_USERNAME} @seximadara I want to tell you a secret!</code>\n\n"
        f"<b>2️⃣ Using User ID:</b>\n"
        f"<code>@{BOT_USERNAME} 2145828547 Meet me in the hidden leaf village tonight!</code>\n\n"
        f"💡 <i>Tip: Click the button below to start writing your whisper instantly!</i></blockquote>"
    )
    
    await message.reply_text(
        text=guide_text,
        parse_mode=ParseMode.HTML,
        reply_markup=switch_btn
    )
    
