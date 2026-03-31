import random
import aiohttp
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ============ WAIFU DATA ============
WAIFUS = [
    {"name": "Zero Two", "anime": "Darling in the FranXX", "rarity": "⭐ Legendary"},
    {"name": "Rem", "anime": "Re:Zero", "rarity": "💎 Rare"},
    {"name": "Asuna", "anime": "Sword Art Online", "rarity": "💎 Rare"},
    {"name": "Mikasa", "anime": "Attack on Titan", "rarity": "⭐ Legendary"},
    {"name": "Hinata", "anime": "Naruto", "rarity": "✨ Common"},
    {"name": "Nezuko", "anime": "Demon Slayer", "rarity": "⭐ Legendary"},
    {"name": "Miku", "anime": "Quintessential Quintuplets", "rarity": "💎 Rare"},
    {"name": "Aqua", "anime": "KonoSuba", "rarity": "✨ Common"},
    {"name": "Erza", "anime": "Fairy Tail", "rarity": "💎 Rare"},
    {"name": "Power", "anime": "Chainsaw Man", "rarity": "⭐ Legendary"},
]

# ============ STORAGE ============
claimed_waifus = {}
active_waifu = {}

# ============ FETCH IMAGE FROM API ============
async def get_waifu_image():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.waifu.pics/sfw/waifu") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("url", None)
    except Exception as e:
        print(f"API Error: {e}")
    return None


# ============ /start COMMAND ============
@Client.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text(
        "**🌸 Waifu Bot is Alive!\n\n"
        "Commands:\n"
        "/waifu — Summon a random waifu\n"
        "/claim — Claim the active waifu\n"
        "/mywaifus — See your collection\n"
        "/waifulb — Leaderboard**"
    )


# ============ /waifu COMMAND ============
@Client.on_message(filters.command("waifu"))
async def send_waifu(client, message):
    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.**")

    chat_id = message.chat.id

    if chat_id in active_waifu:
        w = active_waifu[chat_id]
        return await message.reply_text(
            f"**⚠️ ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴡᴀɪꜰᴜ!\n\n"
            f"「 {w['name']} 」ɪs sᴛɪʟʟ ᴜɴᴄʟᴀɪᴍᴇᴅ!\n"
            f"ᴜsᴇ /ᴄʟᴀɪᴍ ᴏʀ ᴄʟɪᴄᴋ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʜᴇʀ! 💝**"
        )

    loading = await message.reply_text("🌸 **sᴜᴍᴍᴏɴɪɴɢ ᴡᴀɪꜰᴜ...**")

    waifu = random.choice(WAIFUS)
    image_url = await get_waifu_image()
    waifu = dict(waifu)
    waifu["image"] = image_url
    active_waifu[chat_id] = waifu

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💝 ᴄʟᴀɪᴍ", callback_data=f"claim_{chat_id}")]
    ])

    caption = f"""🌸 **ᴀ ᴡᴀɪꜰᴜ ʜᴀs ᴀᴘᴘᴇᴀʀᴇᴅ!**

👤 **ɴᴀᴍᴇ :** {waifu['name']}
🎌 **ᴀɴɪᴍᴇ :** {waifu['anime']}
✨ **ʀᴀʀɪᴛʏ :** {waifu['rarity']}

**ꜰᴀsᴛ! ᴄʟᴀɪᴍ ʜᴇʀ ʙᴇꜰᴏʀᴇ sᴏᴍᴇᴏɴᴇ ᴇʟsᴇ ᴅᴏᴇs! 💝**"""

    await loading.delete()

    try:
        if image_url:
            await message.reply_photo(
                photo=image_url,
                caption=caption,
                reply_markup=buttons
            )
        else:
            await message.reply_text(caption, reply_markup=buttons)
    except Exception as e:
        print(f"Send Error: {e}")
        await message.reply_text(caption, reply_markup=buttons)


# ============ CLAIM BUTTON CALLBACK ============
@Client.on_callback_query(filters.regex(r"^claim_"))
async def claim_callback(client, callback_query):
    chat_id = int(callback_query.data.split("_")[1])
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.mention

    if chat_id not in active_waifu:
        return await callback_query.answer(
            "❌ Already claimed by someone else!", show_alert=True
        )

    waifu = active_waifu.pop(chat_id)

    if user_id not in claimed_waifus:
        claimed_waifus[user_id] = []
    claimed_waifus[user_id].append(waifu)

    await callback_query.answer(
        f"💝 You claimed {waifu['name']}!", show_alert=True
    )

    try:
        await callback_query.message.edit_caption(
            f"""🌸 **ᴡᴀɪꜰᴜ ᴄʟᴀɪᴍᴇᴅ!**

👤 **ɴᴀᴍᴇ :** {waifu['name']}
🎌 **ᴀɴɪᴍᴇ :** {waifu['anime']}
✨ **ʀᴀʀɪᴛʏ :** {waifu['rarity']}

**💝 ᴄʟᴀɪᴍᴇᴅ ʙʏ {user_name}!**"""
        )
    except Exception:
        pass


# ============ /claim COMMAND ============
@Client.on_message(filters.command("claim"))
async def claim_waifu_cmd(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.mention

    if chat_id not in active_waifu:
        return await message.reply_text(
            "**❌ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴡᴀɪꜰᴜ ʀɪɢʜᴛ ɴᴏᴡ!\nᴜsᴇ /ᴡᴀɪꜰᴜ ᴛᴏ sᴜᴍᴍᴏɴ ᴏɴᴇ! 🌸**"
        )

    waifu = active_waifu.pop(chat_id)

    if user_id not in claimed_waifus:
        claimed_waifus[user_id] = []
    claimed_waifus[user_id].append(waifu)

    await message.reply_text(
        f"**💝 {user_name} ʜᴀs ᴄʟᴀɪᴍᴇᴅ {waifu['name']}!\n\n"
        f"sʜᴇ ɪs ɴᴏᴡ ʏᴏᴜʀs! 🎀\n"
        f"ᴜsᴇ /ᴍʏᴡᴀɪꜰᴜs ᴛᴏ sᴇᴇ ʏᴏᴜʀ ᴄᴏʟʟᴇᴄᴛɪᴏɴ! 📖**"
    )


# ============ /mywaifus COMMAND ============
@Client.on_message(filters.command("mywaifus"))
async def my_waifus(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.mention

    if user_id not in claimed_waifus or not claimed_waifus[user_id]:
        return await message.reply_text(
            "**❌ ʏᴏᴜ ʜᴀᴠᴇ ɴᴏ ᴡᴀɪꜰᴜs ʏᴇᴛ!\nᴜsᴇ /ᴡᴀɪꜰᴜ ᴛᴏ sᴜᴍᴍᴏɴ & ᴄʟᴀɪᴍ ᴏɴᴇ! 🌸**"
        )

    waifus = claimed_waifus[user_id]
    waifu_list = "\n".join(
        [f"**{i+1}.** {w['name']} — {w['anime']} {w['rarity']}" for i, w in enumerate(waifus)]
    )

    await message.reply_text(
        f"""📖 **{user_name}'s ᴡᴀɪꜰᴜ ᴄᴏʟʟᴇᴄᴛɪᴏɴ**

{waifu_list}

**ᴛᴏᴛᴀʟ: {len(waifus)} ᴡᴀɪꜰᴜs 💝**"""
    )


# ============ /waifulb LEADERBOARD ============
@Client.on_message(filters.command("waifulb"))
async def waifu_leaderboard(client, message):
    if not claimed_waifus:
        return await message.reply_text("**❌ ɴᴏ ᴏɴᴇ ʜᴀs ᴄʟᴀɪᴍᴇᴅ ᴀɴʏ ᴡᴀɪꜰᴜs ʏᴇᴛ!**")

    sorted_users = sorted(claimed_waifus.items(), key=lambda x: len(x[1]), reverse=True)

    lb_text = "🏆 **ᴡᴀɪꜰᴜ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for i, (user_id, waifus) in enumerate(sorted_users[:10]):
        try:
            user = await client.get_users(user_id)
            name = user.mention
        except Exception:
            name = f"User {user_id}"
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        lb_text += f"{medal} {name} — **{len(waifus)} ᴡᴀɪꜰᴜs**\n"

    await message.reply_text(lb_text)