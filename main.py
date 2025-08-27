import os
import asyncio
import traceback
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest, GetParticipantRequest
from telethon.tl.types import (
    ChannelParticipantAdmin,
    ChannelParticipantCreator
)
from telethon.errors import FloodWaitError

from config import API_ID, API_HASH, SESSION_STRINGS, ALLOWED_USERS

LOGGER_CHAT = -1002987936250  # Logger GC ID

# 🔹 Multiple Clients
clients = [TelegramClient(StringSession(sess), API_ID, API_HASH) for sess in SESSION_STRINGS]

add_count = 0
kick_count = 0


def is_authorized(user_id: int) -> bool:
    return user_id in ALLOWED_USERS


# ==========================================================
# 🔹 Helper: Split List into Chunks
# ==========================================================
def split_chunks(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


# ==========================================================
# 🔹 Worker: Add User
# ==========================================================
async def add_all_worker(client, target_entity, groups, event):
    global add_count
    me = await client.get_me()

    success, failed, no_admin = 0, 0, 0

    for group in groups:
        try:
            # Admin check
            try:
                participant = await client(GetParticipantRequest(group, me.id))
                if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                    no_admin += 1
                    continue
            except:
                no_admin += 1
                continue

            if getattr(group, "megagroup", False):
                await client(InviteToChannelRequest(
                    channel=group,
                    users=[target_entity]
                ))
            else:
                await client(functions.messages.AddChatUserRequest(
                    chat_id=group.id,
                    user_id=target_entity,
                    fwd_limit=10
                ))

            add_count += 1
            success += 1

        except FloodWaitError as e:
            await event.respond(f"⏳ FloodWait {e.seconds}s for {group.title}")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            failed += 1
            await event.respond(f"❌ Failed in {getattr(group, 'title', 'Unknown')}: {e}")

    return success, failed, no_admin


# ==========================================================
# 🔹 Worker: Kick User
# ==========================================================
async def kick_all_worker(client, target_entity, groups, event):
    global kick_count
    me = await client.get_me()

    success, failed, no_admin = 0, 0, 0

    for group in groups:
        try:
            # Admin check
            try:
                participant = await client(GetParticipantRequest(group, me.id))
                if not isinstance(participant.participant, (ChannelParticipantAdmin, ChannelParticipantCreator)):
                    no_admin += 1
                    continue
            except:
                no_admin += 1
                continue

            if getattr(group, "megagroup", False):
                await client.edit_permissions(group, target_entity, view_messages=False)
            else:
                await client(functions.messages.DeleteChatUserRequest(
                    chat_id=group.id,
                    user_id=target_entity
                ))

            kick_count += 1
            success += 1

        except FloodWaitError as e:
            await event.respond(f"⏳ FloodWait {e.seconds}s for {group.title}")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            failed += 1
            await event.respond(f"❌ Failed in {getattr(group, 'title', 'Unknown')}: {e}")

    return success, failed, no_admin


# ==========================================================
# 🔹 Command: Group Add All
# ==========================================================
@clients[0].on(events.NewMessage(pattern=r'/group_add_all(?:\s+(.+))?'))
async def handler_add_all(event):
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
        target_entity = await clients[0].get_entity(target)
        dialogs = await clients[0].get_dialogs()
        groups = [d.entity for d in dialogs if d.is_group or (d.is_channel and getattr(d.entity, "megagroup", False))]

        chunks = split_chunks(groups, len(clients))
        tasks = [add_all_worker(clients[i], target_entity, chunks[i], event) for i in range(len(clients))]
        results = await asyncio.gather(*tasks)

        total_success = sum(r[0] for r in results)
        total_failed = sum(r[1] for r in results)
        total_no_admin = sum(r[2] for r in results)

        summary = (
            f"📊 AddAll Summary for {target}:\n"
            f"✅ Added in {total_success} groups\n"
            f"❌ Failed in {total_failed} groups\n"
            f"⚠️ Skipped {total_no_admin} groups (no admin rights)\n"
            f"📈 Total Adds Count: {add_count}"
        )
        await event.respond(summary)
        await clients[0].send_message(LOGGER_CHAT, summary)

    except Exception as e:
        await event.respond(f"❌ AddAll crashed: {e}")


# ==========================================================
# 🔹 Command: Group Kick All
# ==========================================================
@clients[0].on(events.NewMessage(pattern=r'/group_kick_all(?:\s+(.+))?'))
async def handler_kick_all(event):
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
        target_entity = await clients[0].get_entity(target)
        dialogs = await clients[0].get_dialogs()
        groups = [d.entity for d in dialogs if d.is_group or (d.is_channel and getattr(d.entity, "megagroup", False))]

        chunks = split_chunks(groups, len(clients))
        tasks = [kick_all_worker(clients[i], target_entity, chunks[i], event) for i in range(len(clients))]
        results = await asyncio.gather(*tasks)

        total_success = sum(r[0] for r in results)
        total_failed = sum(r[1] for r in results)
        total_no_admin = sum(r[2] for r in results)

        summary = (
            f"📊 KickAll Summary for {target}:\n"
            f"✅ Kicked from {total_success} groups\n"
            f"❌ Failed in {total_failed} groups\n"
            f"⚠️ Skipped {total_no_admin} groups (no admin rights)\n"
            f"📈 Total Kicks Count: {kick_count}"
        )
        await event.respond(summary)
        await clients[0].send_message(LOGGER_CHAT, summary)

    except Exception as e:
        await event.respond(f"❌ KickAll crashed: {e}")


# ==========================================================
# 🔹 Startup
# ==========================================================
async def main():
    await asyncio.gather(*[client.start() for client in clients])
    await clients[0].send_message(LOGGER_CHAT, f"✅ Multi-ID Userbot started with {len(clients)} accounts!")
    await asyncio.gather(*[client.run_until_disconnected() for client in clients])


print("🚀 Multi-ID Userbot starting...")

try:
    asyncio.run(main())
except Exception as e:
    print(f"❌ Bot crashed: {e}")
