# ----------------------------------------------
# Refer & Earn (Balance system)
# Path: SHUKLAMUSIC/plugins/tools/refer.py
#
# USER COMMANDS
#   /refer  (/earn)            -> refer link, refers, balance, global rank + promotion info
#   /balance                   -> balance, earned, recent activity
#   /pay <id|@user> <amt>      -> transfer balance (or reply: /pay <amt>)
#   daily bonus                -> roz /start karne par balance me bonus
#   /leaderboard (/reftop)     -> Top earners
#   /withdraw upi_id amount    -> UPI withdrawal request (top rankers only)
#   /broadcast  (reply to your content, in bot PM) -> paid promotion
#
# OWNER / SUDO COMMANDS
#   /refconfig                 -> all settings + help
#   /setreward 2               -> Rs per referral
#   /setminwd 300              -> minimum withdrawal
#   /settopwd 3                -> how many top rankers can withdraw
#   /setpromofee 50            -> promotion fee
#   /settop 5                  -> leaderboard size (1-10)
#   /promoapproval on|off      -> owner approves promotions before sending
#   /promotarget users|chats|both
#   /addbalance <id> <amt>  |  /cutbalance <id> <amt>
#   /refuser <id>              -> one user's full stats
#   /pendingwd                 -> pending withdrawal requests
#   /refwipe confirm           -> delete ALL balance-system data
# -----------------------------------------------
import asyncio
import html
import random
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import SUDOERS
from SHUKLAMUSIC.utils.database import (
    get_served_chats,
    get_served_users,
    is_served_user,
)
from config import BANNED_USERS

try:
    from SHUKLAMUSIC.core.mongo import mongodb as db
except ImportError:
    from SHUKLAMUSIC.utils.database import mongodb as db

users = db.rf_users          # _id = user id  {balance, earned, refers, last_earn}
refs = db.rf_refs            # _id = referred user id {referrer, ts, reward}
clicks = db.rf_clicks        # link opens by old users (not counted)
txs = db.rf_tx               # ledger
wds = db.rf_withdrawals      # withdrawal requests
promos = db.rf_promos        # paid promotions
cfg_col = db.rf_settings     # settings + counters

IST = timezone(timedelta(hours=5, minutes=30))
H = ParseMode.HTML
LINE = "━━━━━━━━━━━━━━━━━━"
RANK_EMOJI = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
UPI_RE = re.compile(r"^[a-zA-Z0-9.\-_]{2,64}@[a-zA-Z0-9]{2,32}$")

DEFAULTS = {
    "reward": 2,            # Rs per new referral
    "min_withdraw": 300,
    "top_withdraw": 3,      # only top N earners can withdraw
    "promo_fee": 50,
    "top_size": 5,          # leaderboard size
    "daily_bonus": 1,       # Rs daily bonus (balance only, rank pe asar nahi). 0 = off
    "promo_approval": True, # owner approves promotions first
    "promo_target": "users",  # users | chats | both
}


# ================= small helpers =================
def fm(x) -> str:
    x = float(x)
    return f"{int(x):,}" if x == int(x) else f"{x:,.2f}".rstrip("0").rstrip(".")


def rs(x) -> str:
    return f"₹{fm(x)}"


def now():
    return datetime.now(IST)


def rank_emoji(rank: int) -> str:
    return RANK_EMOJI[rank - 1] if 1 <= rank <= len(RANK_EMOJI) else f"{rank}."


async def get_cfg():
    cfg = dict(DEFAULTS)
    doc = await cfg_col.find_one({"_id": "config"})
    if doc:
        for k in DEFAULTS:
            if k in doc:
                cfg[k] = doc[k]
    return cfg


async def set_cfg(key, value):
    await cfg_col.update_one({"_id": "config"}, {"$set": {key: value}}, upsert=True)


async def next_id(name: str) -> int:
    doc = await cfg_col.find_one_and_update(
        {"_id": f"counter_{name}"},
        {"$inc": {"n": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return doc["n"]


async def ensure_user(uid: int):
    await users.update_one(
        {"_id": uid},
        {"$setOnInsert": {"balance": 0, "earned": 0, "refers": 0, "last_earn": now(), "joined": now()}},
        upsert=True,
    )
    return await users.find_one({"_id": uid})


async def get_rank(uid: int):
    """Global rank (total earnings se). Sabke liye hota hai, 0 earning wale ke liye bhi."""
    u = await users.find_one({"_id": uid})
    if not u:
        return None
    better = await users.count_documents(
        {
            "$or": [
                {"earned": {"$gt": u["earned"]}},
                {"earned": u["earned"], "last_earn": {"$lt": u["last_earn"]}},
            ]
        }
    )
    return better + 1


async def get_top(n: int):
    cur = users.find({"earned": {"$gt": 0}}).sort([("earned", -1), ("last_earn", 1)]).limit(n)
    return await cur.to_list(n)


async def credit(uid: int, amount: float, kind: str, note: str = "") -> str:
    """balance + total earned badhao. 12 digit Txn ID return karta hai."""
    await ensure_user(uid)
    inc = {"balance": amount, "earned": amount}
    if kind == "referral":
        inc["refers"] = 1
    await users.update_one(
        {"_id": uid},
        {"$inc": inc, "$set": {"last_earn": now()}, "$setOnInsert": {"joined": now()}},
        upsert=True,
    )
    txn = "".join(random.choices("0123456789", k=12))
    await txs.insert_one({"txn": txn, "user": uid, "type": kind, "amount": amount, "note": note, "ts": now()})
    return txn


async def debit(uid: int, amount: float, kind: str, note: str = "") -> bool:
    res = await users.update_one(
        {"_id": uid, "balance": {"$gte": amount}}, {"$inc": {"balance": -amount}}
    )
    if res.modified_count != 1:
        return False
    await txs.insert_one({"user": uid, "type": kind, "amount": -amount, "note": note, "ts": now()})
    return True


async def add_balance(uid: int, amount: float, kind: str, note: str = ""):
    """sirf balance badhata hai (total earned / rank nahi)."""
    await ensure_user(uid)
    await users.update_one({"_id": uid}, {"$inc": {"balance": amount}})
    await txs.insert_one({"user": uid, "type": kind, "amount": amount, "note": note, "ts": now()})


async def refund(uid: int, amount: float, note: str = ""):
    await add_balance(uid, amount, "refund", note)


async def uinfo(uid: int):
    """(name, '@username' / 'No Username')"""
    try:
        u = await app.get_users(uid)
        name = html.escape(" ".join(x for x in (u.first_name, u.last_name) if x) or "User")
        uname = f"@{u.username}" if u.username else "No Username"
        return name, uname
    except Exception:
        return "User", "No Username"


async def user_link(uid: int) -> str:
    name, _ = await uinfo(uid)
    return f'<a href="tg://user?id={uid}">{name}</a>'


async def notify(chat_id, text, **kw):
    try:
        await app.send_message(chat_id, text, parse_mode=H, **kw)
    except Exception:
        pass


# ================= 1) capture referral =================
@app.on_message(filters.command("start") & filters.private & ~BANNED_USERS, group=-5)
async def ref_capture(client, message: Message):
    if len(message.command) < 2 or not message.command[1].startswith("ref_"):
        return
    try:
        referrer = int(message.command[1][4:])
    except ValueError:
        return

    user = message.from_user
    if not user or user.is_bot or referrer == user.id:
        return
    if not await is_served_user(referrer):
        return

    # already a bot user -> NOT counted (referrer ko ek baar bata do)
    if await is_served_user(user.id):
        res = await clicks.update_one(
            {"_id": f"{referrer}:{user.id}"},
            {"$setOnInsert": {"referrer": referrer, "user": user.id, "status": "old", "ts": now()}},
            upsert=True,
        )
        if res.upserted_id is not None:
            await notify(
                referrer,
                f"⚠️ <b>{html.escape(user.first_name or 'Someone')}</b> opened your link but already "
                "uses this bot, so <b>no reward</b> was added.\n<i>Only brand-new users count.</i>",
            )
        return

    if await refs.find_one({"_id": user.id}):
        return
    cfg = await get_cfg()
    reward = float(cfg["reward"])
    try:
        await refs.insert_one({"_id": user.id, "referrer": referrer, "ts": now(), "reward": reward})
    except DuplicateKeyError:
        return

    await ensure_user(user.id)
    txn = await credit(referrer, reward, "referral", f"joined:{user.id}")

    try:
        ref_doc = await users.find_one({"_id": referrer})
        rank = await get_rank(referrer)
        s_name = html.escape(" ".join(x for x in (user.first_name, user.last_name) if x) or "User")
        s_un = f"@{user.username}" if user.username else "No Username"
        r_name, r_un = await uinfo(referrer)
        text = (
            "💰 <b>Money Received</b> 🤑\n\n"
            f"{LINE}\n"
            f"💸 <b>Amount:</b> ₹ {fm(reward)}\n"
            f"🧾 <b>Txn ID:</b> <code>{txn}</code>\n"
            f"{LINE}\n\n"
            "📤 <b>Sender</b>\n"
            f"┣ 👤 {s_name}\n"
            f"┣ 🔖 {s_un}\n"
            f"┗ 🆔 <code>{user.id}</code>\n\n"
            "📥 <b>Receiver (You)</b>\n"
            f"┣ 👤 {r_name}\n"
            f"┣ 🔖 {r_un}\n"
            f"┣ 🆔 <code>{referrer}</code>\n"
            f"┣ 🔹 Rank: #{rank if rank else '—'}\n"
            f"┗ 💳 Your New Balance: ₹ {fm(ref_doc['balance'])}\n"
            f"{LINE}\n\n"
            "👉 Withdraw & promotion info: /refer\n"
            "🏆 Leaderboard: /leaderboard"
        )
        await app.send_message(referrer, text, parse_mode=H)
    except Exception:
        pass


# ================= 2) /refer =================
def promo_info_text(bal: float, cfg) -> str:
    fee = float(cfg["promo_fee"])
    status = "✅ You have enough balance!" if bal >= fee else f"❌ Need {rs(fee - bal)} more for promotion"
    return (
        "📢 <b>How to Promote Your Content:</b>\n\n"
        "1️⃣ Send your promotional content here (text/photo/video)\n"
        "2️⃣ Reply to that message with /broadcast\n\n"
        f"💰 Promotion Fee: {rs(fee)}\n"
        f"💳 Your Balance: {rs(bal)}\n"
        f"{status}\n\n"
        "👉 Check leaderboard: /leaderboard"
    )


@app.on_message(filters.command(["refer", "referral", "myref", "earn"]) & ~BANNED_USERS)
async def refer_cmd(client, message: Message):
    uid = message.from_user.id
    cfg = await get_cfg()
    u = await ensure_user(uid)
    rank = await get_rank(uid)
    bal = float(u["balance"])
    link = f"t.me/{app.username}?start=ref_{uid}"

    text = (
        "📥 <b>Your Refer Link</b> 👇👇\n\n"
        f"➥ [ <code>{link}</code> ]\n\n"
        f"👥 <b>Total Refers:</b> {u['refers']}\n"
        f"💰 <b>Total Balance:</b> ₹ {fm(bal)}\n"
        f"👤 <b>Global Rank:</b> #{rank}\n\n"
        f"🤑 You'll earn <b>+{fm(cfg['reward'])} Rupees</b> for every user 🎉\n\n"
        "🎁 <b>Start the bot daily to get daily bonus</b>\n\n"
        f"🎯 You can start promotion in <b>₹ {fm(cfg['promo_fee'])}</b> 🔥\n\n"
        "➲ Check your balance: /balance\n\n"
        "➲ Transfer your balance: /pay\n\n"
        "➲ Withdraw your balance: /withdraw\n\n"
        "➲ Check to users leaderboard: /leaderboard"
    )
    share = f"https://t.me/share/url?url={quote('https://' + link)}&text={quote('🎵 Best music bot! Join using my link')}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Share Refer Link", url=share)]])
    await message.reply_text(text, parse_mode=H, reply_markup=kb)
    await message.reply_text(promo_info_text(bal, cfg), parse_mode=H)


TX_LABEL = {
    "referral": "👥 Referral", "daily": "🎁 Daily bonus", "withdraw": "🏦 Withdraw", "promo": "📢 Promotion",
    "refund": "↩️ Refund", "pay_out": "➡️ Sent", "pay_in": "⬅️ Received", "admin add": "➕ Admin", "admin cut": "➖ Admin",
}


@app.on_message(filters.command("balance") & ~BANNED_USERS)
async def balance_cmd(client, message: Message):
    uid = message.from_user.id
    u = await ensure_user(uid)
    rank = await get_rank(uid)
    not_counted = await clicks.count_documents({"referrer": uid, "status": "old"})
    recent = await txs.find({"user": uid}).sort("ts", -1).limit(5).to_list(5)
    text = (
        "💳 <b>YOUR BALANCE</b>\n\n"
        f"💰 Balance: <b>{rs(u['balance'])}</b>\n"
        f"📈 Total Earned: <b>{rs(u['earned'])}</b>\n"
        f"👥 Total Refers: <b>{u['refers']}</b>\n"
        f"⚠️ Not counted (already bot users): <b>{not_counted}</b>\n"
        f"👤 Global Rank: <b>#{rank}</b>\n"
    )
    if recent:
        text += f"\n🧾 <b>Recent activity</b>\n"
        for t in recent:
            amt = float(t["amount"])
            sign = "+" if amt >= 0 else "-"
            ts = t["ts"]
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            text += f"{TX_LABEL.get(t['type'], t['type'])}: <b>{sign}{rs(abs(amt))}</b> — <i>{ts.astimezone(IST).strftime('%d %b, %I:%M %p')}</i>\n"
    text += "\n➲ Withdraw: /withdraw\n➲ Transfer: /pay\n➲ Refer link: /refer"
    await message.reply_text(text, parse_mode=H)


# ---- daily bonus: roz /start karne par ----
@app.on_message(filters.command("start") & filters.private & ~BANNED_USERS, group=-4)
async def daily_bonus(client, message: Message):
    user = message.from_user
    if not user or user.is_bot:
        return
    cfg = await get_cfg()
    bonus = float(cfg["daily_bonus"])
    if bonus <= 0:
        return
    await ensure_user(user.id)
    today = now().strftime("%Y-%m-%d")
    got = await users.find_one_and_update(
        {"_id": user.id, "last_bonus": {"$ne": today}},
        {"$set": {"last_bonus": today}, "$inc": {"balance": bonus}},
        return_document=ReturnDocument.AFTER,
    )
    if not got:
        return
    await txs.insert_one({"user": user.id, "type": "daily", "amount": bonus, "note": today, "ts": now()})
    try:
        await message.reply_text(
            f"🎁 <b>Daily bonus!</b> +{rs(bonus)} added to your balance.\n💳 Balance: <b>{rs(got['balance'])}</b>\n"
            "<i>Come back tomorrow for more!</i>",
            parse_mode=H,
        )
    except Exception:
        pass


# ---- /pay : balance transfer ----
@app.on_message(filters.command("pay") & ~BANNED_USERS)
async def pay_cmd(client, message: Message):
    uid = message.from_user.id
    usage = (
        "💸 <b>Transfer your balance</b>\n\n"
        "<code>/pay user_id amount</code>\n<code>/pay @username amount</code>\n"
        "ya kisi ke message pe reply karke: <code>/pay amount</code>"
    )
    args = message.command[1:]
    target = None
    try:
        if message.reply_to_message and message.reply_to_message.from_user and len(args) == 1:
            target, amt_s = message.reply_to_message.from_user.id, args[0]
        elif len(args) == 2:
            who, amt_s = args
            if who.lstrip("-").isdigit():
                target = int(who)
            else:
                target = (await client.get_users(who.lstrip("@"))).id
        else:
            return await message.reply_text(usage, parse_mode=H)
        amount = round(float(amt_s.replace("₹", "")), 2)
    except Exception:
        return await message.reply_text("❌ User ya amount galat hai.\n\n" + usage, parse_mode=H)

    if amount < 1:
        return await message.reply_text("❌ Minimum transfer <b>₹1</b> hai.", parse_mode=H)
    if target == uid:
        return await message.reply_text("❌ Apne aap ko pay nahi kar sakte.")
    if not await is_served_user(target):
        return await message.reply_text("❌ Is user ne abhi tak bot start nahi kiya.")

    await ensure_user(uid)
    if not await debit(uid, amount, "pay_out", f"to:{target}"):
        u = await ensure_user(uid)
        return await message.reply_text(f"❌ Not enough balance. Your balance: <b>{rs(u['balance'])}</b>", parse_mode=H)
    await add_balance(target, amount, "pay_in", f"from:{uid}")

    me = await user_link(uid)
    to = await user_link(target)
    u = await ensure_user(uid)
    await message.reply_text(
        f"✅ <b>{rs(amount)}</b> sent to {to}.\n💳 Your balance: <b>{rs(u['balance'])}</b>", parse_mode=H
    )
    await notify(target, f"💰 <b>{rs(amount)}</b> received from {me}!\nCheck: /balance")


# ================= 3) /leaderboard =================
@app.on_message(filters.command(["leaderboard", "reftop", "refboard"]) & ~BANNED_USERS)
async def leaderboard_cmd(client, message: Message):
    try:
        cfg = await get_cfg()
        n = int(cfg["top_size"])
        top = await get_top(n)
        text = f"🏆 <b>Top {n} Earners Leaderboard</b>\n{LINE}\n\n"
        if not top:
            text += "No earners yet. Be the first! 🚀\n\n"
        for i, row in enumerate(top, start=1):
            text += (
                f"{rank_emoji(i)} <b>Rank #{i}</b>\n"
                f"┣ 🆔 <code>{row['_id']}</code>\n"
                f"┣ 💳 Current Balance: {rs(row['balance'])}\n"
                f"┣ 📈 Total Earned: {rs(row['earned'])}\n"
                f"┗ 👥 Total Refers: {row['refers']}\n"
                f"{LINE}\n\n"
            )
        uid = message.from_user.id
        u = await ensure_user(uid)
        rank = await get_rank(uid)
        text += (
            f"💳 Your Balance: <b>{rs(u['balance'])}</b>\n"
            f"{rank_emoji(rank) if rank and rank <= 10 else '🏅'} Your Rank: <b>{('#' + str(rank)) if rank else '—'}</b>\n\n"
            "👉 Your link & withdraw info: /refer"
        )
        await message.reply_text(text, parse_mode=H)
    except Exception as e:
        await message.reply_text(
            f"⚠️ Leaderboard error:\n<code>{html.escape(type(e).__name__ + ': ' + str(e))}</code>",
            parse_mode=H,
        )


# ================= 4) /withdraw =================
def wd_text(wd, status_line=None) -> str:
    st = {"pending": "🕒 Pending", "paid": "✅ Paid", "rejected": "❌ Rejected"}[wd["status"]]
    return (
        f"💸 <b>Withdrawal #{wd['_id']}</b>\n{LINE}\n"
        f"👤 User: <a href=\"tg://user?id={wd['user']}\">{wd['user']}</a>\n"
        f"🏦 UPI: <code>{html.escape(wd['upi'])}</code>\n"
        f"💰 Amount: <b>{rs(wd['amount'])}</b>\n"
        f"📌 Status: {st}"
        + (f"\n{status_line}" if status_line else "")
    )


def wd_buttons(wid: int):
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✅ Mark Paid", callback_data=f"rfwd:paid:{wid}"),
            InlineKeyboardButton("❌ Reject (refund)", callback_data=f"rfwd:rej:{wid}"),
        ]]
    )


@app.on_message(filters.command("withdraw") & filters.private & ~BANNED_USERS)
async def withdraw_cmd(client, message: Message):
    uid = message.from_user.id
    cfg = await get_cfg()
    usage = (
        "📋 <b>Correct Format:</b>\n<code>/withdraw upi_id amount</code>\n\n"
        "Example:\n<code>/withdraw name@upi 500</code>"
    )
    if len(message.command) == 1:
        u0 = await ensure_user(uid)
        rank0 = await get_rank(uid)
        bal0 = float(u0["balance"])
        if rank0 is not None and rank0 <= int(cfg["top_withdraw"]) and float(u0["earned"]) > 0 and bal0 >= float(cfg["min_withdraw"]):
            st = "✅ <b>You can withdraw now!</b>"
        elif rank0 is None or rank0 > int(cfg["top_withdraw"]) or float(u0["earned"]) <= 0:
            st = f"❌ Withdrawal locked: reach top {cfg['top_withdraw']} (your rank: #{rank0})"
        else:
            st = f"❌ Need {rs(float(cfg['min_withdraw']) - bal0)} more to withdraw"
        return await message.reply_text(
            "🏦 <b>WITHDRAW MONEY IN BANK/UPI</b>\n\n" + usage + "\n\n"
            f"{LINE}\n"
            f"• ✅ Minimum withdrawal: <b>{rs(cfg['min_withdraw'])}</b>\n"
            f"• 🏆 Only top <b>{cfg['top_withdraw']}</b> rankers can withdraw\n"
            "• 📊 Rank is based on total earnings\n"
            f"{LINE}\n\n"
            f"💳 Your Balance: <b>{rs(bal0)}</b>\n"
            f"🏅 Your Rank: <b>#{rank0}</b>\n\n{st}\n\n"
            "👉 Check leaderboard: /leaderboard",
            parse_mode=H,
        )
    if len(message.command) != 3:
        return await message.reply_text(usage, parse_mode=H)
    upi = message.command[1].strip()
    try:
        amount = round(float(message.command[2]), 2)
    except ValueError:
        return await message.reply_text(usage, parse_mode=H)
    if not UPI_RE.match(upi) or amount <= 0:
        return await message.reply_text("❌ Invalid UPI ID or amount.\n\n" + usage, parse_mode=H)

    u = await ensure_user(uid)
    rank = await get_rank(uid)
    if amount < float(cfg["min_withdraw"]):
        return await message.reply_text(f"❌ Minimum withdrawal is <b>{rs(cfg['min_withdraw'])}</b>.", parse_mode=H)
    if rank is None or rank > int(cfg["top_withdraw"]) or float(u["earned"]) <= 0:
        return await message.reply_text(
            f"🏆 Only top <b>{cfg['top_withdraw']}</b> rankers can withdraw.\n"
            f"Your rank: <b>#{rank}</b>\n\nCheck: /leaderboard",
            parse_mode=H,
        )
    if float(u["balance"]) < amount:
        return await message.reply_text(f"❌ Not enough balance. Your balance: <b>{rs(u['balance'])}</b>", parse_mode=H)
    if await wds.find_one({"user": uid, "status": "pending"}):
        return await message.reply_text("⏳ You already have a pending withdrawal. Please wait for it to be processed.")

    if not await debit(uid, amount, "withdraw", upi):
        return await message.reply_text("❌ Not enough balance.")
    wid = await next_id("wd")
    wd = {"_id": wid, "user": uid, "upi": upi, "amount": amount, "status": "pending", "ts": now()}
    await wds.insert_one(wd)

    await message.reply_text(
        f"✅ <b>Withdrawal request #{wid} submitted!</b>\n\n"
        f"💰 Amount: <b>{rs(amount)}</b>\n🏦 UPI: <code>{html.escape(upi)}</code>\n\n"
        "The amount is held. You will get a message once the owner pays it.",
        parse_mode=H,
    )
    await notify(config.OWNER_ID, "🔔 <b>New withdrawal request</b>\n\n" + wd_text(wd), reply_markup=wd_buttons(wid))
    if config.LOGGER_ID != config.OWNER_ID:
        await notify(config.LOGGER_ID, "🔔 <b>New withdrawal request</b>\n\n" + wd_text(wd))


@app.on_callback_query(filters.regex(r"^rfwd:(paid|rej):(\d+)$") & SUDOERS)
async def wd_callback(client, cq: CallbackQuery):
    action, wid = cq.matches[0].group(1), int(cq.matches[0].group(2))
    new_status = "paid" if action == "paid" else "rejected"
    wd = await wds.find_one_and_update(
        {"_id": wid, "status": "pending"},
        {"$set": {"status": new_status, "by": cq.from_user.id, "done": now()}},
        return_document=ReturnDocument.AFTER,
    )
    if not wd:
        return await cq.answer("Already processed.", show_alert=True)
    if new_status == "rejected":
        await refund(wd["user"], wd["amount"], f"withdraw #{wid} rejected")
        await notify(wd["user"], f"❌ <b>Withdrawal #{wid} rejected.</b>\n{rs(wd['amount'])} has been added back to your balance.")
    else:
        await notify(
            wd["user"],
            f"✅ <b>Withdrawal #{wid} paid!</b>\n\n💰 {rs(wd['amount'])} sent to <code>{html.escape(wd['upi'])}</code>.\nThank you! 💖",
        )
    try:
        await cq.message.edit_text(wd_text(wd, f"👮 By: {cq.from_user.mention}"), parse_mode=H)
    except Exception:
        pass
    await cq.answer("Done ✅")


@app.on_message(filters.command("pendingwd") & SUDOERS)
async def pending_wd(client, message: Message):
    items = await wds.find({"status": "pending"}).sort("_id", 1).to_list(50)
    if not items:
        return await message.reply_text("✅ No pending withdrawals.")
    for wd in items:
        await message.reply_text(wd_text(wd), parse_mode=H, reply_markup=wd_buttons(wd["_id"]))


# ================= 5) paid promotion (/broadcast by normal users) =================
@app.on_message(filters.command("broadcast") & filters.private & ~SUDOERS & ~BANNED_USERS)
async def promo_request(client, message: Message):
    uid = message.from_user.id
    cfg = await get_cfg()
    fee = float(cfg["promo_fee"])
    u = await ensure_user(uid)
    if not message.reply_to_message:
        return await message.reply_text(promo_info_text(float(u["balance"]), cfg), parse_mode=H)
    if float(u["balance"]) < fee:
        return await message.reply_text(
            f"❌ Not enough balance.\n💰 Fee: <b>{rs(fee)}</b>\n💳 Your balance: <b>{rs(u['balance'])}</b>", parse_mode=H
        )
    kb = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton(f"✅ Confirm ({rs(fee)})", callback_data=f"rfp:y:{message.reply_to_message.id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="rfp:n"),
        ]]
    )
    target = {"users": "all bot users", "chats": "all groups", "both": "all users & groups"}[cfg["promo_target"]]
    await message.reply_text(
        f"📢 <b>Promotion</b>\n\nYour message will be sent to <b>{target}</b>.\n"
        f"💰 Fee: <b>{rs(fee)}</b> (deducted from your balance)\n"
        + ("🕒 It will be sent after owner approval (fee refunded if rejected).\n" if cfg["promo_approval"] else ""),
        parse_mode=H,
        reply_markup=kb,
    )


@app.on_callback_query(filters.regex(r"^rfp:(y|n)(?::(\d+))?$"))
async def promo_confirm(client, cq: CallbackQuery):
    if cq.matches[0].group(1) == "n":
        return await cq.message.edit_text("❌ Promotion cancelled.")
    uid = cq.from_user.id
    msg_id = int(cq.matches[0].group(2))
    cfg = await get_cfg()
    fee = float(cfg["promo_fee"])

    try:
        content = await client.get_messages(uid, msg_id)
        if content.empty:
            raise ValueError
    except Exception:
        return await cq.message.edit_text("❌ Your content message was not found. Please send it again.")

    if not await debit(uid, fee, "promo", f"msg:{msg_id}"):
        return await cq.message.edit_text(f"❌ Not enough balance (need {rs(fee)}).")

    pid = await next_id("promo")
    approval = bool(cfg["promo_approval"])
    await promos.insert_one(
        {
            "_id": pid, "user": uid, "msg_id": msg_id, "fee": fee, "target": cfg["promo_target"],
            "status": "pending" if approval else "approved", "ts": now(),
        }
    )
    if approval:
        await cq.message.edit_text(f"✅ <b>Promotion #{pid} submitted!</b>\n\n{rs(fee)} deducted. You'll be notified after approval.", parse_mode=H)
        try:
            await client.copy_message(config.OWNER_ID, uid, msg_id)
        except Exception:
            pass
        kb = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("✅ Approve & Send", callback_data=f"rfpa:ok:{pid}"),
                InlineKeyboardButton("❌ Reject (refund)", callback_data=f"rfpa:no:{pid}"),
            ]]
        )
        await notify(
            config.OWNER_ID,
            f"📢 <b>Promotion request #{pid}</b>\n👤 {await user_link(uid)} (<code>{uid}</code>)\n"
            f"💰 Fee paid: {rs(fee)}\n🎯 Target: {cfg['promo_target']}\n\n⬆️ Content shown above.",
            reply_markup=kb,
        )
    else:
        await cq.message.edit_text(f"🚀 <b>Promotion #{pid} started!</b>\n{rs(fee)} deducted.", parse_mode=H)
        asyncio.create_task(run_promo(pid))
    await cq.answer()


@app.on_callback_query(filters.regex(r"^rfpa:(ok|no):(\d+)$") & SUDOERS)
async def promo_admin_cb(client, cq: CallbackQuery):
    action, pid = cq.matches[0].group(1), int(cq.matches[0].group(2))
    new_status = "approved" if action == "ok" else "rejected"
    pr = await promos.find_one_and_update(
        {"_id": pid, "status": "pending"}, {"$set": {"status": new_status}}, return_document=ReturnDocument.AFTER
    )
    if not pr:
        return await cq.answer("Already processed.", show_alert=True)
    if new_status == "rejected":
        await refund(pr["user"], pr["fee"], f"promo #{pid} rejected")
        await notify(pr["user"], f"❌ <b>Promotion #{pid} rejected.</b>\n{rs(pr['fee'])} refunded to your balance.")
        result = "❌ Rejected & refunded"
    else:
        await notify(pr["user"], f"✅ <b>Promotion #{pid} approved!</b> Sending now...")
        asyncio.create_task(run_promo(pid))
        result = "✅ Approved, sending"
    try:
        await cq.message.edit_text(f"📢 <b>Promotion #{pid}</b> — {result}", parse_mode=H)
    except Exception:
        pass
    await cq.answer("Done")


async def run_promo(pid: int):
    pr = await promos.find_one({"_id": pid})
    if not pr:
        return
    targets = []
    if pr["target"] in ("users", "both"):
        targets += [int(x["user_id"]) for x in await get_served_users()]
    if pr["target"] in ("chats", "both"):
        targets += [int(x["chat_id"]) for x in await get_served_chats()]
    targets = list(dict.fromkeys(targets))

    sent = failed = 0
    for t in targets:
        for attempt in range(2):
            try:
                await app.copy_message(t, pr["user"], pr["msg_id"])
                sent += 1
                break
            except FloodWait as fw:
                await asyncio.sleep(min(int(fw.value), 60))
            except Exception:
                failed += 1
                break
        await asyncio.sleep(0.3)

    await promos.update_one({"_id": pid}, {"$set": {"status": "done", "sent": sent, "failed": failed}})
    await notify(pr["user"], f"📢 <b>Promotion #{pid} finished!</b>\n✅ Delivered: <b>{sent}</b>\n❌ Failed: <b>{failed}</b>")
    await notify(config.OWNER_ID, f"📢 Promotion #{pid} done. Delivered: {sent}, failed: {failed}")


# ================= 6) owner settings =================
async def cfg_text() -> str:
    c = await get_cfg()
    return (
        "⚙️ <b>REFERRAL SETTINGS</b>\n\n"
        f"💸 Reward per referral: <b>{rs(c['reward'])}</b>\n"
        f"🏦 Minimum withdrawal: <b>{rs(c['min_withdraw'])}</b>\n"
        f"🏆 Top rankers who can withdraw: <b>{c['top_withdraw']}</b>\n"
        f"📢 Promotion fee: <b>{rs(c['promo_fee'])}</b>\n"
        f"📊 Leaderboard size: <b>{c['top_size']}</b>\n"
        f"🎁 Daily bonus: <b>{rs(c['daily_bonus'])}</b> (0 = off)\n"
        f"🕒 Promotion approval: <b>{'ON' if c['promo_approval'] else 'OFF'}</b>\n"
        f"🎯 Promotion target: <b>{c['promo_target']}</b>\n\n"
        "<b>Commands</b>\n"
        "<code>/setreward 2</code> — har referral ke ₹\n"
        "<code>/setminwd 300</code> — minimum withdrawal\n"
        "<code>/settopwd 3</code> — top kitne log withdraw kar sakte\n"
        "<code>/setpromofee 50</code> — promotion fee\n"
        "<code>/settop 5</code> — leaderboard size (1-10)\n"
        "<code>/setdaily 1</code> — daily bonus ₹ (0 = off)\n"
        "<code>/promoapproval on|off</code>\n"
        "<code>/promotarget users|chats|both</code>\n"
        "<code>/addbalance ID 50</code> | <code>/cutbalance ID 50</code>\n"
        "<code>/refuser ID</code> — kisi user ki details\n"
        "<code>/pendingwd</code> — pending withdrawals\n"
        "<code>/refwipe confirm</code> — saara data delete"
    )


@app.on_message(filters.command("refconfig") & SUDOERS)
async def refconfig_cmd(client, message: Message):
    await message.reply_text(await cfg_text(), parse_mode=H)


def _num_setter(command: str, key: str, label: str, integer=False, minimum=0, maximum=None):
    @app.on_message(filters.command(command) & SUDOERS)
    async def _h(client, message: Message):
        try:
            v = float(message.command[1].replace("₹", "").replace(",", ""))
            if integer:
                v = int(v)
            assert v >= minimum and (maximum is None or v <= maximum)
        except Exception:
            return await message.reply_text(f"Usage: <code>/{command} 10</code>", parse_mode=H)
        await set_cfg(key, v)
        await message.reply_text(f"✅ {label} updated.\n\n" + await cfg_text(), parse_mode=H)


_num_setter("setreward", "reward", "Reward", minimum=0)
_num_setter("setminwd", "min_withdraw", "Minimum withdrawal", minimum=1)
_num_setter("settopwd", "top_withdraw", "Top withdraw ranks", integer=True, minimum=1, maximum=100)
_num_setter("setpromofee", "promo_fee", "Promotion fee", minimum=0)
_num_setter("settop", "top_size", "Leaderboard size", integer=True, minimum=1, maximum=10)
_num_setter("setdaily", "daily_bonus", "Daily bonus", minimum=0)


@app.on_message(filters.command("promoapproval") & SUDOERS)
async def promoapproval_cmd(client, message: Message):
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg not in ("on", "off"):
        return await message.reply_text("Usage: <code>/promoapproval on</code> ya <code>off</code>", parse_mode=H)
    await set_cfg("promo_approval", arg == "on")
    await message.reply_text("✅ Updated.\n\n" + await cfg_text(), parse_mode=H)


@app.on_message(filters.command("promotarget") & SUDOERS)
async def promotarget_cmd(client, message: Message):
    arg = message.command[1].lower() if len(message.command) > 1 else ""
    if arg not in ("users", "chats", "both"):
        return await message.reply_text("Usage: <code>/promotarget users</code> | <code>chats</code> | <code>both</code>", parse_mode=H)
    await set_cfg("promo_target", arg)
    await message.reply_text("✅ Updated.\n\n" + await cfg_text(), parse_mode=H)


@app.on_message(filters.command(["addbalance", "cutbalance"]) & SUDOERS)
async def balance_admin(client, message: Message):
    cmd = message.command[0].lower()
    try:
        uid = int(message.command[1])
        amount = round(float(message.command[2]), 2)
        assert amount > 0
    except Exception:
        return await message.reply_text(f"Usage: <code>/{cmd} USER_ID 50</code>", parse_mode=H)
    if cmd == "addbalance":
        await refund(uid, amount, "admin add")
        await notify(uid, f"🎁 <b>{rs(amount)}</b> added to your balance by admin.")
        msg = f"✅ Added {rs(amount)}"
    else:
        if not await debit(uid, amount, "admin cut", "admin"):
            return await message.reply_text("❌ User ke paas itna balance nahi hai.")
        await notify(uid, f"➖ <b>{rs(amount)}</b> deducted from your balance by admin.")
        msg = f"✅ Deducted {rs(amount)}"
    u = await ensure_user(uid)
    await message.reply_text(f"{msg}\n💳 New balance: <b>{rs(u['balance'])}</b>", parse_mode=H)


@app.on_message(filters.command("refuser") & SUDOERS)
async def refuser_cmd(client, message: Message):
    try:
        uid = int(message.command[1])
    except Exception:
        return await message.reply_text("Usage: <code>/refuser USER_ID</code>", parse_mode=H)
    u = await users.find_one({"_id": uid})
    if not u:
        return await message.reply_text("User ka koi data nahi mila.")
    rank = await get_rank(uid)
    not_counted = await clicks.count_documents({"referrer": uid, "status": "old"})
    pending = await wds.count_documents({"user": uid, "status": "pending"})
    ref_by = await refs.find_one({"_id": uid})
    await message.reply_text(
        f"👤 {await user_link(uid)} (<code>{uid}</code>)\n{LINE}\n"
        f"💳 Balance: <b>{rs(u['balance'])}</b>\n📈 Total Earned: <b>{rs(u['earned'])}</b>\n"
        f"👥 Refers: <b>{u['refers']}</b>\n⚠️ Not counted: <b>{not_counted}</b>\n"
        f"🏅 Rank: <b>{('#' + str(rank)) if rank else '—'}</b>\n🕒 Pending withdrawals: <b>{pending}</b>\n"
        f"🔗 Joined via: <code>{ref_by['referrer'] if ref_by else '—'}</code>",
        parse_mode=H,
    )


@app.on_message(filters.command("refwipe") & SUDOERS)
async def refwipe_cmd(client, message: Message):
    if len(message.command) < 2 or message.command[1].lower() != "confirm":
        return await message.reply_text(
            "⚠️ Ye <b>saare</b> balances, referrals, withdrawals aur promotions delete kar dega.\n"
            "Pakka karna hai to: <code>/refwipe confirm</code>",
            parse_mode=H,
        )
    for col in (users, refs, clicks, txs, wds, promos):
        await col.delete_many({})
    await message.reply_text("🧹 Balance-system ka saara data delete ho gaya. Settings safe hain.")


# ================= 7) startup: purane weekly system ka data hatao + indexes =================
async def _startup():
    try:
        done = await cfg_col.find_one({"_id": "old_system_purged"})
        if not done:
            for name in ("referrals", "referral_clicks", "referral_meta"):
                await db.drop_collection(name)
            await cfg_col.insert_one({"_id": "old_system_purged", "ts": now()})
        await users.create_index([("earned", -1), ("last_earn", 1)])
        await refs.create_index("referrer")
        await clicks.create_index("referrer")
        await wds.create_index([("user", 1), ("status", 1)])
    except Exception:
        pass


try:
    asyncio.get_running_loop().create_task(_startup())
except RuntimeError:
    asyncio.get_event_loop().create_task(_startup())
