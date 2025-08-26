import os
import traceback
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import DeleteChatUserRequest
from config import API_ID, API_HASH, SESSION_STRING, ALLOWED_USERS

LOGGER_CHAT = -1002987936250  # Logger GC ID

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

add_count = 0
kick_count = 0


def is_authorized(user_id: int) -> bool:
    return user_id in ALLOWED_USERS


# ---------------------- GROUP ADD ----------------------
@client.on(events.NewMessage(pattern=r'/group_add(?:\s+(.+))?'))
async def handler_add(event):
    global add_count
    if not is_authorized(event.sender_id):
        return

    # user resolve
    if event.is_reply and not event.pattern_match.group(1):
        reply_msg = await event.get_reply_message()
        user = reply_msg.sender_id
    else:
        user = event.pattern_match.group(1)

    try:
        group = await client.get_entity(event.chat_id)
        user_entity = await client.get_entity(user)

        if getattr(group, "megagroup", False) or getattr(group, "broadcast", False):
            # For supergroup / channel
            await client(InviteToChannelRequest(
                channel=group,
                users=[user_entity]
            ))
        else:
            # For old small groups
            await client(functions.messages.AddChatUserRequest(
                chat_id=event.chat_id,
                user_id=user_entity,
                fwd_limit=10
            ))

        add_count += 1
        await event.respond(f"✅ {user} added!\n📊 Total Adds: {add_count}")

    except Exception as e:
        await event.respond(f"❌ Add failed: {e}")


# ---------------------- GROUP KICK ----------------------
@client.on(events.NewMessage(pattern=r'/group_kick(?:\s+(.+))?'))
async def handler_kick(event):
    global kick_count
    if not is_authorized(event.sender_id):
        return

    # user resolve
    if event.is_reply and not event.pattern_match.group(1):
        reply_msg = await event.get_reply_message()
        user = reply_msg.sender_id
    else:
        user = event.pattern_match.group(1)

    try:
        group = await client.get_entity(event.chat_id)
        user_entity = await client.get_entity(user)

        if getattr(group, "megagroup", False) or getattr(group, "broadcast", False):
            # For supergroup / channel → restrict (kick)
            await client.edit_permissions(group, user_entity, view_messages=False)
        else:
            # For normal small groups
            await client(DeleteChatUserRequest(
                chat_id=event.chat_id,
                user_id=user_entity
            ))

        kick_count += 1
        await event.respond(f"✅ {user} kicked!\n📊 Total Kicks: {kick_count}")

    except Exception as e:
        await event.respond(f"❌ Kick failed: {e}")


# ---------------------- GROUP ADD TO ALL ----------------------
@client.on(events.NewMessage(pattern=r'/group_add_all(?:\s+(.+))?'))
async def handler_add_all(event):
    global add_count
    if not is_authorized(event.sender_id):
        return

    # user resolve
    if event.is_reply and not event.pattern_match.group(1):
        reply_msg = await event.get_reply_message()
        user = reply_msg.sender_id
    else:
        user = event.pattern_match.group(1)

    try:
        user_entity = await client.get_entity(user)
        dialogs = await client.get_dialogs()

        success, failed = 0, 0

        for dialog in dialogs:
            if dialog.is_group or dialog.is_channel:
                try:
                    group = await client.get_entity(dialog.entity)

                    if getattr(group, "megagroup", False) or getattr(group, "broadcast", False):
                        await client(InviteToChannelRequest(
                            channel=group,
                            users=[user_entity]
                        ))
                    else:
                        await client(functions.messages.AddChatUserRequest(
                            chat_id=group.id,
                            user_id=user_entity,
                            fwd_limit=10
                        ))

                    success += 1
                except Exception as e:
                    failed += 1
                    await event.respond(f"❌ Failed in {dialog.name}: {e}")

        add_count += success
        await event.respond(
            f"✅ Added {user} to {success} groups.\n"
            f"❌ Failed in {failed} groups.\n"
            f"📊 Total Adds: {add_count}"
        )

    except Exception as e:
        await event.respond(f"❌ AddAll failed: {e}")


# ---------------------- MAKE GROUP ----------------------
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


# ---------------------- EVAL ----------------------
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


# ---------------------- STARTUP ----------------------
async def main():
    await client.send_message(LOGGER_CHAT, "✅ Userbot started and connected successfully!")


print("🚀 Userbot starting...")

try:
    client.start()
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
except Exception as e:
    print(f"❌ Bot crashed: {e}")
