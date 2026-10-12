# ----------------------------------------------
# Refer & Earn — Weekly Leaderboard (fully configurable from the bot)
# Path: SHUKLAMUSIC/plugins/tools/refer.py
#
# USER COMMANDS
#   /refer        -> your link + detailed stats (counted / not counted / recent)
#   /leaderboard  -> this week's top 10 + prizes  (also /reftop)
#
# OWNER / SUDO COMMANDS  (no code change needed, settings saved in MongoDB)
#   /refconfig                      -> show current settings + help
#   /setwinners <n>                 -> how many winners (1-10)
#   /setprize <rank> <text>         -> prize text for a rank   (use "none" to clear)
#   /setmin <rank> <number>         -> minimum referrals for that rank (500, 1k, 2.5k ...)
#   /setperref <rank> <amount>      -> Rs paid PER referral to that rank winner (0 = off)
#   /refreset                       -> back to default settings
#   /refwinners [now]               -> last week's winners (or live ranking)
# -----------------------------------------------
import asyncio
import copy
import html
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from pymongo.errors import DuplicateKeyError
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from SHUKLAMUSIC import app
from SHUKLAMUSIC.misc import SUDOERS
from SHUKLAMUSIC.utils.database import is_served_user
from config import BANNED_USERS

try:
    from SHUKLAMUSIC.core.mongo import mongodb as db
except ImportError:
    from SHUKLAMUSIC.utils.database import mongodb as db

refs = db.referrals            # counted referrals (_id = referred user id)
clicks = db.referral_clicks    # link opens that were NOT counted (old users)
meta = db.referral_meta        # settings + last announced week

IST = timezone(timedelta(hours=5, minutes=30))
MAX_WINNERS = 10
MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

DEFAULT_CFG = {
    "winner_count": 3,
    "ranks": {
        "1": {"prize": "1 Telegram ID", "min": 50, "per_ref": 0},
        "2": {"prize": "₹15", "min": 40, "per_ref": 0},
        "3": {"prize": "₹8", "min": 30, "per_ref": 0},
    },
}


# ================= settings helpers =================
def _blank_rank():
    return {"prize": "", "min": 1, "per_ref": 0}


async def get_cfg():
    cfg = copy.deepcopy(DEFAULT_CFG)
    for i in range(4, MAX_WINNERS + 1):
        cfg["ranks"][str(i)] = _blank_rank()
    doc = await meta.find_one({"_id": "config"})
    if doc:
        if "winner_count" in doc:
            cfg["winner_count"] = max(1, min(MAX_WINNERS, int(doc["winner_count"])))
        for k, v in (doc.get("ranks") or {}).items():
            if k in cfg["ranks"]:
                cfg["ranks"][k].update(v)
    return cfg


async def save_rank_field(rank: int, field: str, value):
    await meta.update_one(
        {"_id": "config"}, {"$set": {f"ranks.{rank}.{field}": value}}, upsert=True
    )


def parse_num(text: str) -> float:
    s = text.strip().lower().replace(",", "").replace("₹", "")
    mult = 1
    if s.endswith("k"):
        mult, s = 1000, s[:-1]
    elif s.endswith("m"):
        mult, s = 1_000_000, s[:-1]
    return float(s) * mult


def fm(x) -> str:
    """money / number -> clean string"""
    x = float(x)
    return f"{int(x):,}" if x == int(x) else f"{x:,.2f}".rstrip("0").rstrip(".")


def medal(rank: int) -> str:
    return MEDALS.get(rank, f"{rank}.")


def active_ranks(cfg):
    return [(i, cfg["ranks"][str(i)]) for i in range(1, cfg["winner_count"] + 1)]


def prize_label(r) -> str:
    parts = []
    if r["prize"]:
        parts.append(html.escape(r["prize"]))
    if float(r["per_ref"]) > 0:
        parts.append(f"₹{fm(r['per_ref'])} per referral")
    return " + ".join(parts) or "—"


def prize_info(cfg) -> str:
    lines = []
    for i, r in active_ranks(cfg):
        lines.append(f"{medal(i)} <b>{prize_label(r)}</b>  <i>(min {fm(r['min'])} refs)</i>")
    return "\n".join(lines)


def payout_text(r, count: int) -> str:
    parts = []
    if r["prize"]:
        parts.append(html.escape(r["prize"]))
    if float(r["per_ref"]) > 0:
        total = float(r["per_ref"]) * count
        parts.append(f"₹{fm(total)} ({count}×₹{fm(r['per_ref'])})")
    return " + ".join(parts) or "—"


# ================= time helpers =================
def week_key(dt: datetime = None) -> str:
    dt = dt or datetime.now(IST)
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def prev_week_key() -> str:
    return week_key(datetime.now(IST) - timedelta(days=7))


def time_left() -> str:
    now = datetime.now(IST)
    nxt = (now + timedelta(days=7 - now.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    d = nxt - now
    h, rem = divmod(d.seconds, 3600)
    return f"{d.days}d {h}h {rem // 60}m"


def fmt_ts(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IST).strftime("%d %b, %I:%M %p")


# ================= data helpers =================
async def get_top(week: str, limit: int = 10):
    pipeline = [
        {"$match": {"week": week}},
        {"$group": {"_id": "$referrer", "count": {"$sum": 1}, "last": {"$max": "$ts"}}},
        {"$sort": {"count": -1, "last": 1}},  # tie -> who reached it first wins
        {"$limit": limit},
    ]
    return await refs.aggregate(pipeline).to_list(limit)


async def user_link(uid: int) -> str:
    try:
        u = await app.get_users(uid)
        name = html.escape(u.first_name or "User")
        return f'<a href="tg://user?id={uid}">{name}</a>'
    except Exception:
        return f"<code>{uid}</code>"


async def winners_text(week: str, title: str) -> str:
    cfg = await get_cfg()
    top = await get_top(week, max(10, cfg["winner_count"]))
    text = f"🏆 <b>{title}</b>\n📅 <code>{week}</code>\n\n"
    if not top:
        return text + "No referrals this week."
    for i, row in enumerate(top, start=1):
        who = await user_link(row["_id"])
        line = f"{medal(i)} {who} — <b>{row['count']}</b>"
        if i <= cfg["winner_count"]:
            r = cfg["ranks"][str(i)]
            if row["count"] >= int(r["min"]):
                line += (
                    f"\n    ✅ Eligible: <b>{payout_text(r, row['count'])}</b>"
                    f" (ID: <code>{row['_id']}</code>)"
                )
            else:
                line += f"\n    ❌ Not eligible (needs {fm(r['min'])}, has {row['count']})"
        text += line + "\n"
    return text


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

    # already a bot user -> NOT counted (but we remember + tell the referrer once)
    if await is_served_user(user.id):
        res = await clicks.update_one(
            {"_id": f"{referrer}:{user.id}"},
            {
                "$setOnInsert": {
                    "referrer": referrer,
                    "user": user.id,
                    "status": "old",
                    "ts": datetime.now(IST),
                }
            },
            upsert=True,
        )
        if res.upserted_id is not None:
            try:
                await app.send_message(
                    referrer,
                    f"⚠️ <b>{html.escape(user.first_name or 'Someone')}</b> opened your link "
                    "but already uses this bot, so it was <b>not counted</b>.\n"
                    "<i>Only brand-new users count.</i>",
                    parse_mode=ParseMode.HTML,
                )
            except Exception:
                pass
        return

    if await refs.find_one({"_id": user.id}):
        return
    try:
        await refs.insert_one(
            {
                "_id": user.id,
                "referrer": referrer,
                "week": week_key(),
                "ts": datetime.now(IST),
            }
        )
    except DuplicateKeyError:
        return

    try:
        count = await refs.count_documents({"referrer": referrer, "week": week_key()})
        await app.send_message(
            referrer,
            f"🎉 <b>New referral counted!</b>\n"
            f"{html.escape(user.first_name or 'Someone')} joined using your link.\n"
            f"📊 This week: <b>{count}</b> referrals",
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        pass


# ================= 2) /refer =================
@app.on_message(filters.command(["refer", "referral", "myref"]) & ~BANNED_USERS)
async def refer_cmd(client, message: Message):
    uid = message.from_user.id
    link = f"https://t.me/{app.username}?start=ref_{uid}"
    wk = week_key()
    cfg = await get_cfg()

    week_count = await refs.count_documents({"referrer": uid, "week": wk})
    total = await refs.count_documents({"referrer": uid})
    not_counted = await clicks.count_documents({"referrer": uid, "status": "old"})
    top = await get_top(wk, 1000)
    rank = next((i for i, r in enumerate(top, 1) if r["_id"] == uid), None)

    # progress line
    if rank and rank <= cfg["winner_count"]:
        r = cfg["ranks"][str(rank)]
        need = int(r["min"]) - week_count
        if need <= 0:
            status = f"✅ You qualify for rank #{rank} prize right now!"
        else:
            status = f"🎯 Rank #{rank}: need <b>{fm(need)}</b> more to qualify (min {fm(r['min'])})"
    else:
        status = f"🎯 Reach the top {cfg['winner_count']} and hit the minimum to win."

    recent = await refs.find({"referrer": uid}).sort("ts", -1).limit(5).to_list(5)
    recent_txt = ""
    if recent:
        recent_txt = "\n🕒 <b>Recent referrals</b>\n"
        for row in recent:
            who = await user_link(row["_id"])
            recent_txt += f"• {who} — <i>{fmt_ts(row['ts'])}</i>\n"

    text = (
        "💸 <b>REFER & EARN</b>\n\n"
        f"Invite friends and win weekly prizes! (Top {cfg['winner_count']})\n\n"
        f"{prize_info(cfg)}\n\n"
        f"🔗 <b>Your link:</b>\n<code>{link}</code>\n\n"
        f"📊 <b>Your stats</b>\n"
        f"✅ Counted this week: <b>{week_count}</b>\n"
        f"👥 Counted all time: <b>{total}</b>\n"
        f"⚠️ Not counted (already bot users): <b>{not_counted}</b>\n"
        f"🔗 Total link joins: <b>{total + not_counted}</b>\n"
        f"🏅 Your rank this week: <b>{rank if rank else '—'}</b>\n"
        f"{status}\n"
        f"⏳ Week ends in: <b>{time_left()}</b>\n"
        f"{recent_txt}\n"
        "<i>Only new users who start the bot via your link are counted. "
        "Every week starts from 0.</i>"
    )
    share = f"https://t.me/share/url?url={quote(link)}&text={quote('🎵 Best music bot! Join using my link')}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("📤 Share Link", url=share)]])
    await message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)


# ================= 3) /leaderboard =================
@app.on_message(filters.command(["leaderboard", "reftop", "refboard"]) & ~BANNED_USERS)
async def leaderboard_cmd(client, message: Message):
    try:
        wk = week_key()
        cfg = await get_cfg()
        top = await get_top(wk, 10)

        text = (
            f"🏆 <b>WEEKLY REFERRAL LEADERBOARD</b>\n"
            f"📅 <code>{wk}</code>  |  ⏳ {time_left()} left\n\n"
        )
        if not top:
            text += "No referrals yet this week. Be the first! 🚀\n"
        else:
            for i, row in enumerate(top, start=1):
                who = await user_link(row["_id"])
                text += f"{medal(i)} {who} — <b>{row['count']}</b>\n"

        text += f"\n🎁 <b>Prizes</b>\n{prize_info(cfg)}\n\nUse /refer to get your link."
        await message.reply_text(text, parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply_text(
            f"⚠️ Leaderboard error:\n<code>{html.escape(type(e).__name__ + ': ' + str(e))}</code>",
            parse_mode=ParseMode.HTML,
        )


# ================= 4) owner settings =================
HELP = (
    "\n<b>Commands</b>\n"
    "<code>/setwinners 1</code> — kitne winners (1-10)\n"
    "<code>/setprize 1 ₹500 + Telegram ID</code> — rank 1 ka prize\n"
    "<code>/setmin 1 500</code> — rank 1 ke min referrals (1k, 2.5k bhi chalega)\n"
    "<code>/setperref 1 1</code> — rank 1 ko har referral ka ₹1 (0 = off)\n"
    "<code>/setprize 2 none</code> — prize text hatane ke liye\n"
    "<code>/refreset</code> — default settings\n"
    "<code>/refwinners</code> — pichle hafte ke winners"
)


async def cfg_text(cfg) -> str:
    text = f"⚙️ <b>REFERRAL SETTINGS</b>\n\n🏆 Winners: <b>{cfg['winner_count']}</b>\n\n"
    for i in range(1, MAX_WINNERS + 1):
        r = cfg["ranks"][str(i)]
        on = i <= cfg["winner_count"]
        if not on and not r["prize"] and float(r["per_ref"]) == 0:
            continue
        text += (
            f"{'🟢' if on else '⚪️'} {medal(i)} Rank {i}: <b>{prize_label(r)}</b>\n"
            f"     min <b>{fm(r['min'])}</b> refs{'' if on else '  <i>(disabled)</i>'}\n"
        )
    return text


def _parse_rank(message: Message):
    try:
        rank = int(message.command[1])
    except (IndexError, ValueError):
        return None
    return rank if 1 <= rank <= MAX_WINNERS else None


@app.on_message(filters.command("refconfig") & SUDOERS)
async def refconfig_cmd(client, message: Message):
    cfg = await get_cfg()
    await message.reply_text(await cfg_text(cfg) + HELP, parse_mode=ParseMode.HTML)


@app.on_message(filters.command("setwinners") & SUDOERS)
async def setwinners_cmd(client, message: Message):
    try:
        n = int(message.command[1])
        assert 1 <= n <= MAX_WINNERS
    except Exception:
        return await message.reply_text(
            f"Usage: <code>/setwinners 1</code> (1 se {MAX_WINNERS})", parse_mode=ParseMode.HTML
        )
    await meta.update_one({"_id": "config"}, {"$set": {"winner_count": n}}, upsert=True)
    cfg = await get_cfg()
    warn = ""
    for i in range(1, n + 1):
        r = cfg["ranks"][str(i)]
        if not r["prize"] and float(r["per_ref"]) == 0:
            warn += f"\n⚠️ Rank {i} ka prize set nahi hai: <code>/setprize {i} ...</code>"
    await message.reply_text(
        "✅ Winners updated.\n\n" + await cfg_text(cfg) + warn, parse_mode=ParseMode.HTML
    )


@app.on_message(filters.command("setprize") & SUDOERS)
async def setprize_cmd(client, message: Message):
    rank = _parse_rank(message)
    parts = message.text.split(None, 2)
    if rank is None or len(parts) < 3:
        return await message.reply_text(
            "Usage: <code>/setprize 1 ₹500 + Telegram ID</code>", parse_mode=ParseMode.HTML
        )
    text = parts[2].strip()
    if text.lower() in ("none", "off", "-", "clear"):
        text = ""
    await save_rank_field(rank, "prize", text)
    cfg = await get_cfg()
    await message.reply_text("✅ Prize updated.\n\n" + await cfg_text(cfg), parse_mode=ParseMode.HTML)


@app.on_message(filters.command("setmin") & SUDOERS)
async def setmin_cmd(client, message: Message):
    rank = _parse_rank(message)
    try:
        value = int(parse_num(message.command[2]))
        assert value >= 1
    except Exception:
        rank = None
    if rank is None:
        return await message.reply_text(
            "Usage: <code>/setmin 1 500</code>  (1k, 2.5k bhi chalega)", parse_mode=ParseMode.HTML
        )
    await save_rank_field(rank, "min", value)
    cfg = await get_cfg()
    await message.reply_text("✅ Minimum updated.\n\n" + await cfg_text(cfg), parse_mode=ParseMode.HTML)


@app.on_message(filters.command("setperref") & SUDOERS)
async def setperref_cmd(client, message: Message):
    rank = _parse_rank(message)
    try:
        value = float(parse_num(message.command[2]))
        assert value >= 0
    except Exception:
        rank = None
    if rank is None:
        return await message.reply_text(
            "Usage: <code>/setperref 1 1</code>  (rank 1 ko har referral ka ₹1, 0 = off)",
            parse_mode=ParseMode.HTML,
        )
    await save_rank_field(rank, "per_ref", value)
    cfg = await get_cfg()
    await message.reply_text(
        "✅ Per-referral reward updated.\n\n" + await cfg_text(cfg), parse_mode=ParseMode.HTML
    )


@app.on_message(filters.command("refreset") & SUDOERS)
async def refreset_cmd(client, message: Message):
    await meta.update_one(
        {"_id": "config"}, {"$unset": {"winner_count": "", "ranks": ""}}, upsert=True
    )
    cfg = await get_cfg()
    await message.reply_text("♻️ Settings reset.\n\n" + await cfg_text(cfg), parse_mode=ParseMode.HTML)


@app.on_message(filters.command("refwinners") & SUDOERS)
async def refwinners_cmd(client, message: Message):
    if len(message.command) > 1 and message.command[1].lower() == "now":
        txt = await winners_text(week_key(), "THIS WEEK (LIVE)")
    else:
        txt = await winners_text(prev_week_key(), "LAST WEEK WINNERS")
    await message.reply_text(txt, parse_mode=ParseMode.HTML)


# ================= 5) auto announce winners every Monday =================
async def _weekly_announcer():
    try:
        await refs.create_index("week")
        await refs.create_index("referrer")
        await clicks.create_index("referrer")
    except Exception:
        pass

    while True:
        try:
            prev = prev_week_key()
            doc = await meta.find_one({"_id": "last_announced"})
            if not doc:
                await meta.update_one(
                    {"_id": "last_announced"}, {"$set": {"week": prev}}, upsert=True
                )
            elif doc["week"] != prev:
                txt = await winners_text(prev, "WEEKLY WINNERS")
                txt += "\n💰 <i>Pay the eligible winners manually.</i>"
                for chat in {config.OWNER_ID, config.LOGGER_ID}:
                    try:
                        await app.send_message(chat, txt, parse_mode=ParseMode.HTML)
                    except Exception:
                        pass
                await meta.update_one(
                    {"_id": "last_announced"}, {"$set": {"week": prev}}, upsert=True
                )
        except Exception:
            pass
        await asyncio.sleep(300)


try:
    asyncio.get_running_loop().create_task(_weekly_announcer())
except RuntimeError:
    asyncio.get_event_loop().create_task(_weekly_announcer())

