import os
import traceback
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from config import API_ID, API_HASH, SESSION_STRING, ALLOWED_USERS

LOGGER_CHAT = -1002987936250  # Logger GC ID

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

add_count = 0
kick_count = 0


def is_authorized(user_id: int) -> bool:
    return user_id in ALLOWED_USERS


@client.on(events.NewMessage(pattern=r'/group_add(?:\s+(.+))?'))
async def handler_add(event):
    global add_count
    if not is_authorized(event.sender_id):
        return
    if event.is_reply and not event.pattern_match.group(1):
        reply_msg = await event.get_reply_message()
        user = reply_msg.sender_id
    else:
        user = event.pattern_match.group(1)
    try:
        await client(functions.messages.AddChatUserRequest(
            chat_id=event.chat_id,
            user_id=user,
            fwd_limit=10
        ))
        add_count += 1
        await event.respond(f"✅ {user} added!\n📊 Total Adds: {add_count}")
    except Exception as e:
        await event.respond(f"❌ Add failed: {e}")


@client.on(events.NewMessage(pattern=r'/group_kick(?:\s+(.+))?'))
async def handler_kick(event):
    global kick_count
    if not is_authorized(event.sender_id):
        return
    if event.is_reply and not event.pattern_match.group(1):
        reply_msg = await event.get_reply_message()
        user = reply_msg.sender_id
    else:
        user = event.pattern_match.group(1)
    try:
        await client.edit_permissions(event.chat_id, user, view_messages=False)
        kick_count += 1
        await event.respond(f"✅ {user} kicked!\n📊 Total Kicks: {kick_count}")
    except Exception as e:
        await event.respond(f"❌ Kick failed: {e}")


@client.on(events.NewMessage(pattern=r'/make_group (\d+)'))
async def handler_make_group(event):
    if not is_authorized(event.sender_id):
        return

    n = int(event.pattern_match.group(1))
    if n > 100:
        await event.respond("⚠️ Limit 100 groups at a time.")
        return

    for i in range(n):
        title = f"My_Private_Group_{i+1}"
        try:
            await client(functions.messages.CreateChatRequest(
                users=[event.sender_id, "MissRose_bot"],  # Add Rose bot automatically
                title=title
            ))
            await event.respond(f"✅ Group '{title}' created with @MissRose_bot")
        except Exception as e:
            await event.respond(f"❌ Group create failed: {e}")


@client.on(events.NewMessage(pattern=r'/eval (.+)', outgoing=True))
async def handler_eval(event):
    if not is_authorized(event.sender_id):
        return
    code = event.pattern_match.group(1)
    try:
        result = eval(code)
        if callable(result):
            result = result()
        await event.respond(f"🖥️ Result:\n{result}")
    except Exception:
        await event.respond(f"❌ Error:\n{traceback.format_exc()}")


async def main():
    await client.send_message(LOGGER_CHAT, "✅ Userbot started and connected successfully!")


print("🚀 Userbot starting...")

try:
    client.start()
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
except Exception as e:
    print(f"❌ Bot crashed: {e}")
