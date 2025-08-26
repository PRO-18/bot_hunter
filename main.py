import os
import traceback
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest, GetParticipantRequest
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantCreator
)
from config import API_ID, API_HASH, SESSION_STRING, ALLOWED_USERS

LOGGER_CHAT = -1002987936250  # Logger GC ID

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

add_count = 0
kick_count = 0


def is_authorized(user_id: int) -> bool:
    return user_id in ALLOWED_USERS


# ==========================================================
# 🔹 Group Add All
# ==========================================================
@client.on(events.NewMessage(pattern=r'/group_add_all(?:\s+(.+))?'))
async def handler_add_all(event):
    global add_count
    if not is_authorized(event.sender_id):
        return

    if event.is_reply and not event.pattern_match.group(1):
        reply_msg = await event.get_reply_message()
        target = reply_msg.sender_id
    else:
        target = event.pattern_match.group(1)

    if not target:
        await event.respond("⚠️ Usage: `/group_add_all @username` ya reply karke use karo.")
        return

    try:
        me = await client.get_me()
        target_entity = await client.get_entity(target)
        dialogs = await client.get_dialogs()

        success, failed, no_admin = 0, 0, 0

        for dialog in dialogs:
            if dialog.is_group or (dialog.is_channel and getattr(dialog.entity, "megagroup", False)):
                try:
                    group = await client.get_entity(dialog.entity)

                    # Bot admin check
                    try:
                        participant = await client(GetParticipantRequest(group, me.id))
                        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                            no_admin += 1
                            continue
                    except:
                        no_admin += 1
                        continue

                    # Supergroup
                    if getattr(group, "megagroup", False):
                        await client(InviteToChannelRequest(
                            channel=group,
                            users=[target_entity]
                        ))
                    else:
                        # Normal group
                        await client(functions.messages.AddChatUserRequest(
                            chat_id=group.id,
                            user_id=target_entity,
                            fwd_limit=10
                        ))

                    add_count += 1
                    success += 1
                    await event.respond(f"✅ {target} added in {dialog.name}")

                except Exception as e:
                    failed += 1
                    await event.respond(f"❌ Failed in {dialog.name}: {e}")

        await event.respond(
            f"📊 AddAll Summary for {target}:\n"
            f"✅ Added in {success} groups\n"
            f"❌ Failed in {failed} groups\n"
            f"⚠️ Skipped {no_admin} groups (no admin rights)\n"
            f"📈 Total Adds Count: {add_count}"
        )

    except Exception as e:
        await event.respond(f"❌ AddAll crashed: {e}")


# ==========================================================
# 🔹 Group Kick All
# ==========================================================
@client.on(events.NewMessage(pattern=r'/group_kick_all(?:\s+(.+))?'))
async def handler_kick_all(event):
    global kick_count
    if not is_authorized(event.sender_id):
        return

    if event.is_reply and not event.pattern_match.group(1):
        reply_msg = await event.get_reply_message()
        target = reply_msg.sender_id
    else:
        target = event.pattern_match.group(1)

    if not target:
        await event.respond("⚠️ Usage: `/group_kick_all @username` ya reply karke use karo.")
        return

    try:
        me = await client.get_me()
        target_entity = await client.get_entity(target)
        dialogs = await client.get_dialogs()

        success, failed, no_admin = 0, 0, 0

        for dialog in dialogs:
            if dialog.is_group or (dialog.is_channel and getattr(dialog.entity, "megagroup", False)):
                try:
                    group = await client.get_entity(dialog.entity)

                    # Bot admin check
                    try:
                        participant = await client(GetParticipantRequest(group, me.id))
                        if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                            no_admin += 1
                            continue
                    except:
                        no_admin += 1
                        continue

                    # Supergroup
                    if getattr(group, "megagroup", False):
                        await client.edit_permissions(group, target_entity, view_messages=False)
                    else:
                        # Normal group
                        await client(functions.messages.DeleteChatUserRequest(
                            chat_id=group.id,
                            user_id=target_entity
                        ))

                    kick_count += 1
                    success += 1
                    await event.respond(f"✅ {target} kicked from {dialog.name}")

                except Exception as e:
                    failed += 1
                    await event.respond(f"❌ Failed in {dialog.name}: {e}")

        await event.respond(
            f"📊 KickAll Summary for {target}:\n"
            f"✅ Kicked from {success} groups\n"
            f"❌ Failed in {failed} groups\n"
            f"⚠️ Skipped {no_admin} groups (no admin rights)\n"
            f"📈 Total Kicks Count: {kick_count}"
        )

    except Exception as e:
        await event.respond(f"❌ KickAll crashed: {e}")


# ==========================================================
# 🔹 Startup
# ==========================================================
async def main():
    await client.send_message(LOGGER_CHAT, "✅ Userbot started and connected successfully!")


print("🚀 Userbot starting...")

try:
    client.start()
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
except Exception as e:
    print(f"❌ Bot crashed: {e}")
