# -----------------------------------------------
# 🔸 StrangerMusic Project
# 🔹 Developed & Maintained by: Shashank Shukla (https://github.com/itzshukla)
# -----------------------------------------------
import random
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from SHUKLAMUSIC import app

def calculate_gay_percentage():
    return random.randint(1, 100)

def generate_gay_response(gay_percentage):
    if gay_percentage < 30:
        return "You're straight as an arrow. 🏳️‍🌈"
    elif 30 <= gay_percentage < 70:
        return "You might have a bit of a rainbow in you. 🌈"
    else:
        return "You're shining with rainbow colors! 🌟🏳️‍🌈"

@app.on_message(filters.command("gay"))
def gay_calculator_command(client, message: Message):
    gay_percentage = calculate_gay_percentage()
    gay_response = generate_gay_response(gay_percentage)
    message.reply_text(
        f"<blockquote>🏳️‍🌈 <b>Gay Calculator</b>\n\n"
        f"<b>Percentage:</b> <code>{gay_percentage}%</code>\n"
        f"<b>Result:</b> {gay_response}</blockquote>",
        parse_mode=ParseMode.HTML
    )


@app.on_message(filters.command("logo"))
async def logo_command(client, msg: Message):
    if len(msg.command) == 1:
        return await msg.reply_text(
            "<blockquote>❌ <b>Usage:</b>\n\n<code>/logo STRANGER</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
    
    logo_name = msg.text.split(" ", 1)[1].strip()
    m = await msg.reply_text("<blockquote>🎨 <b>Creating your logo, please wait...</b></blockquote>", parse_mode=ParseMode.HTML)
    
    # ⚠️ Note: api.sdbots.tech is currently down. Agar aapke paas koi dusri working API ho toh URL yahan change karein.
    API = f"https://api.sdbots.tech/logohq?text={logo_name}"
    
    try:
        response = requests.get(API, timeout=10)
        if response.status_code != 200:
            return await m.edit_text("<blockquote>❌ <b>Logo API is currently down! Try again later.</b></blockquote>", parse_mode=ParseMode.HTML)
        
        req = response.url
        await msg.reply_photo(
            photo=req,
            caption=f"<blockquote>✨ <b>Logo Generated for:</b> <code>{logo_name}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        await m.delete()
    except Exception as e:
        await m.edit_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>", parse_mode=ParseMode.HTML)


@app.on_message(filters.command("animelogo"))
async def anime_logo_command(client, msg: Message):
    if len(msg.command) == 1:
        return await msg.reply_text(
            "<blockquote>❌ <b>Usage:</b>\n\n<code>/animelogo STRANGER</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
    
    logo_name = msg.text.split(" ", 1)[1].strip()
    m = await msg.reply_text("<blockquote>🌸 <b>Creating anime logo, please wait...</b></blockquote>", parse_mode=ParseMode.HTML)
    
    API = f"https://api.sdbots.tech/anime-logo?name={logo_name}"
    
    try:
        response = requests.get(API, timeout=10)
        if response.status_code != 200:
            return await m.edit_text("<blockquote>❌ <b>Anime Logo API is currently down! Try again later.</b></blockquote>", parse_mode=ParseMode.HTML)
        
        req = response.url
        await msg.reply_photo(
            photo=req,
            caption=f"<blockquote>✨ <b>Anime Logo Generated for:</b> <code>{logo_name}</code></blockquote>",
            parse_mode=ParseMode.HTML
        )
        await m.delete()
    except Exception as e:
        await m.edit_text(f"<blockquote>❌ <b>Error:</b> <code>{e}</code></blockquote>", parse_mode=ParseMode.HTML)
        
