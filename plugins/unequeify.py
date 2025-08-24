# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import re, asyncio
from database import Db, db
from config import temp
from .test import CLIENT, get_client
from script import Script
from pyrogram import Client, filters, enums 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, MessageNotModified

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

CLIENT = CLIENT()
COMPLETED_BTN = InlineKeyboardMarkup(
  [[
    InlineKeyboardButton('💟 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ 💟', url='https://t.me/VJ_Bot_Disscussion')
  ],[
    InlineKeyboardButton('💠 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 💠', url='https://t.me/vj_botz')
  ]]
)
CANCEL_BTN = InlineKeyboardMarkup([[InlineKeyboardButton('• ᴄᴀɴᴄᴇʟ', 'terminate_frwd')]])

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

async def safe_edit_message(message, text, reply_markup=None):
    """Safely edit message handling MessageNotModified error"""
    try:
        await message.edit(text, reply_markup=reply_markup)
    except MessageNotModified:
        # Message is already up to date, we can safely ignore this error
        pass
    except Exception as e:
        # For other errors, you might want to handle them differently
        raise e

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

@Client.on_message(filters.command("unequify") & filters.private)
async def unequify(client, message):
   user_id = message.from_user.id
   temp.CANCEL[user_id] = False
   
   if temp.lock.get(user_id) and str(temp.lock.get(user_id)) == "True":
      return await message.reply("**Please wait until previous task completes**")
   
   _bot = await db.get_userbot(user_id)
   if not _bot:
      return await message.reply("<b>Need userbot to do this process. Please add a userbot using /settings</b>")
   
   target = await client.ask(user_id, text="**Forward the last message from target chat or send last message link.**\n/cancel - `cancel this process`")
   
   if target.text and target.text.startswith("/cancel"):
      return await message.reply("**Process cancelled!**")
   elif target.text:
      regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
      match = regex.match(target.text.replace("?single", ""))
      if not match:
         return await message.reply('**Invalid link**')
      chat_id = match.group(4)
      last_msg_id = int(match.group(5))
      if chat_id.isnumeric():
         chat_id = int(("-100" + chat_id))
   elif target.forward_from_chat.type in [enums.ChatType.CHANNEL, 'supergroup']:
        last_msg_id = target.forward_from_message_id
        chat_id = target.forward_from_chat.username or target.forward_from_chat.id
   else:
        return await message.reply_text("**Invalid input!**")
   
   confirm = await client.ask(user_id, text="**Send /yes to start the process and /no to cancel this process**")
   if confirm.text.lower() == '/no':
      return await confirm.reply("**Process cancelled!**")
   
   sts = await confirm.reply("`Processing...`")
   il = False
   data = _bot['session']
   
   try:
      bot = await get_client(data, is_bot=il)
      await bot.start()
   except Exception as e:
      return await sts.edit(f"**Error starting userbot:** {e}")
   
   # Check if userbot is admin in target chat with delete permissions
   try:
       me = await bot.get_me()
       try:
           status = await bot.get_chat_member(chat_id, me.id)
           privileges = getattr(status, "privileges", None)
           if privileges:
               can_delete_messages = getattr(privileges, "can_delete_messages", False)
           else:
               can_delete_messages = False
       except:
           can_delete_messages = False
           
       if not can_delete_messages:
           await sts.edit(f"**Please make your [userbot](t.me/{_bot['username']}) admin in target chat with delete permissions**")
           return await bot.stop()
   except Exception as e:
       await sts.edit(f"**Error checking admin status:** {e}")
       return await bot.stop()
   
   # Start the duplicate removal process
   unique_files = set()
   duplicates_count = 0
   total_count = 0
   temp.lock[user_id] = True
   temp.CANCEL[user_id] = False
   
   try:
     await safe_edit_message(sts, Script.DUPLICATE_TEXT.format(total_count, duplicates_count, "Starting..."), reply_markup=CANCEL_BTN)
     
     # Iterate through messages
     async for message in bot.search_messages(chat_id=chat_id, filter=enums.MessagesFilter.DOCUMENT):
        if temp.CANCEL.get(user_id) == True:
           await safe_edit_message(sts, Script.DUPLICATE_TEXT.format(total_count, duplicates_count, "Cancelled"), reply_markup=COMPLETED_BTN)
           return await bot.stop()
        
        if message and message.document:
            file_unique_id = message.document.file_unique_id
            
            if file_unique_id in unique_files:
                # This is a duplicate
                try:
                    await bot.delete_messages(chat_id, message.id)
                    duplicates_count += 1
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                except Exception as e:
                    print(f"Error deleting message {message.id}: {e}")
            else:
                unique_files.add(file_unique_id)
            
            total_count += 1
            
            # Update status every 100 messages
            if total_count % 100 == 0:
                await safe_edit_message(sts, Script.DUPLICATE_TEXT.format(total_count, duplicates_count, "Processing..."), reply_markup=CANCEL_BTN)
                
   except Exception as e:
       temp.lock[user_id] = False 
       await sts.edit(f"**ERROR**\n`{e}`")
       return await bot.stop()
   
   temp.lock[user_id] = False
   await safe_edit_message(sts, Script.DUPLICATE_TEXT.format(total_count, duplicates_count, "Completed"), reply_markup=COMPLETED_BTN)
   await bot.stop()

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
