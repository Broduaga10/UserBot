from time import sleep
from pyrogram import Client, filters, enums
from pyrogram.raw.functions.contacts import ResolveUsername
from json import loads

import os.path
import logging

read1 = open("C:\\Users\\micro\\PycharmProjects\\UserBot_Telegram\\userbot_files\\config.cfg",
             'r', encoding='UTF-8', errors='replace')
txt1 = read1.read()
read1.close()
cfg1 = loads(txt1)

api_id = cfg1["api_id"]
api_hash = cfg1["api_hash"]

del read1, txt1, cfg1

app = Client("my_account", api_id=api_id, api_hash=api_hash)
logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")


@app.on_message(filters.me)
def get_id(client, message):
    chat_id = message.chat.id
    message_id = message.id
    user_id = int(message.from_user.id)

    def editText(edittxt):
        app.edit_message_text(chat_id=chat_id, message_id=message_id, text=edittxt)

    read = open("C:\\Users\\micro\\PycharmProjects\\UserBot_Telegram\\userbot_files\\config.cfg",
                'r', encoding='UTF-8', errors='replace')
    txt = read.read()
    read.close()
    cfg = loads(txt)
    del txt

    prefix = cfg["prefix"]
    prefixDel = cfg["prefixdel"]
    path = cfg["path"]
    save_path = cfg["save_path"]

    try:
        mess = message.text.split()
    except:
        logging.error(f"message.text.split() - {message.text}")
        return

    if mess[0] in prefixDel:
        if len(mess) == 1:
            message.delete()
            if message.reply_to_message is None:
                for message in app.get_chat_history(chat_id):
                    if message and int(message.from_user.id) == user_id:
                        app.delete_messages(chat_id=message.chat.id, message_ids=int(message.id))
                        return

            else:
                app.delete_messages(chat_id=chat_id, message_ids=message.reply_to_message_id)
        else:
            try:
                mess[1] = int(mess[1])
            except:
                return
            message.delete()

            number = 0
            for message in app.get_chat_history(chat_id):
                if number < mess[1]:
                    if message is not None and message.from_user.id == user_id:
                        app.delete_messages(chat_id=chat_id, message_ids=message.id)
                        number += 1
                else:
                    break

    if not mess[0].lower() in prefix:
        return
    mess = mess[1:]
    if len(mess) < 1:
        return
    command = mess[0].lower()
    commands = cfg["commands"]

    if command in commands["time"]:
        try:
            editText(f"{message.date}")
        except:
            logging.error("TIME ERROR")
            message.delete()
    elif command in commands["user"]:
        try:
            username = mess[1][1:]
        except IndexError:
            username = message.reply_to_message.from_user.username
        except:
            editText('**Wrong username**')
            return

        try:
            user_info = client.get_chat_member(chat_id=chat_id,
                                               user_id=client.invoke(
                                                   ResolveUsername(username=username)).peer.user_id)
        except:
            try:
                user_info = client.invoke(ResolveUsername(username=username)).users[0]
            except:
                editText('**This user does not exist**')
                return
        res_dict = loads(str(user_info))

        if str(user_info.status).split('.')[1] in ["MEMBER", "OWNER", "ADMINISTRATOR", "RESTRICTED"]:
            result = f"<pre>User:</pre>\n**Name:** <a href=\"tg://user?id={user_info.user.id}\">" \
                     f"{user_info.user.first_name}</a>" \
                     f"\n**Username:** {user_info.user.username}" \
                     f"\n**ID:** {user_info.user.id}" \
                     f"\n**Premium:** {user_info.user.is_premium}" \
                     f"\n**Contact:** {user_info.user.is_contact}" \
                     f"\n\n<pre>Chat:</pre>" \
                     f"\n**Title:** {message.chat.title}" \
                     f"\n**Chat ID:** {chat_id}" \
                     f"\n**Joined Date:** {user_info.joined_date}"

            if user_info.restricted_by is not None:
                result += "\n\n<pre>Restricted by:</pre>" \
                          f"\n**Name:** <a href=\"tg://user?id={user_info.restricted_by.id}\">" \
                          f"{user_info.restricted_by.first_name}</a>" \
                          f"\n**Username:** {user_info.restricted_by.username}" \
                          f"\n**ID:** {user_info.restricted_by.id}" \
                          f"\n**Premium:** {user_info.restricted_by.is_premium}" \
                          f"\n**Contact:** {user_info.restricted_by.is_contact}"

            if user_info.permissions is not None:
                result += f"\n\n<pre>Chat Permissions:</pre>" \
                          f"\n**Status:** {str(user_info.status).split('.')[1].lower()}" \
                          f"\n**Send messages:** {user_info.permissions.can_send_messages}" \
                          f"\n**Change info:** {user_info.permissions.can_change_info}" \
                          f"\n**Send polls:** {user_info.permissions.can_send_polls}" \
                          f"\n**Invite users:** {user_info.permissions.can_invite_users}" \
                          f"\n**Pin messages:** {user_info.permissions.can_pin_messages}"
        elif str(message.chat.type).split('.')[1] == 'PRIVATE':
            result = f"<pre>User:</pre>\n**Name:** <a href=\"tg://user?id={res_dict['id']}\">" \
                     f"{res_dict['first_name']}</a>" \
                     f"\n**Username:** {res_dict['username']}" \
                     f"\n**ID:** {res_dict['id']}" \
                     f"\n**Premium:** {res_dict['premium']}" \
                     f"\n**Contact:** {res_dict['contact']}"
            try:
                result += f"\n**Phone Number:** ||{res_dict['phone']}||"
            except:
                result += f"\n**Phone Number:** ||hidden||"
        elif res_dict["_"].split('.')[1] == "User":
            result = f"<pre>User:</pre>\n**Name:** <a href=\"tg://user?id={res_dict['id']}\">" \
                     f"{res_dict['first_name']}</a>" \
                     f"\n**Username:** {res_dict['username']}" \
                     f"\n**ID:** {res_dict['id']}" \
                     f"\n**Premium:** {res_dict['premium']}" \
                     f"\n**Contact:** {res_dict['contact']}"

        editText(result)
    elif command in commands["admins"]:
        try:
            administrators = []
            for adm in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
                administrators.append(adm)

            i = len(administrators)
            result = "<pre>Admins:</pre>"

            for i in range(i):
                if str(administrators[i].status) != "ChatMemberStatus.OWNER":
                    result += f"\n**Owner** <a href=\"tg://user?id={administrators[i].user.id}\">" \
                              f"{administrators[i].user.first_name}</a>"
                else:
                    result += f"\n**Admin:** <a href=\"tg://user?id={administrators[i].user.id}\">" \
                              f"{administrators[i].user.first_name}</a>"
            if result == "<pre>Admins:</pre>":
                result += "\n__Empty__"
            editText(result)
        except:
            editText("**Can't get admins**")
            return
    elif command in commands["new_msg"]:
        reply = message.reply_to_message
        if reply is None:
            editText("**Use the command in response to the post**")
            return
        name = message.text.split(mess[0])[1][1:]
        if name == '':
            editText(f"**Enter the title**")
            return

        if reply.media is None or str(reply.media) == "MessageMediaType.WEB_PAGE":
            read = open(f'{path}/message.txt', 'r', encoding='UTF-8', errors='replace')
            lines = read.readlines()
            read.close()
            for line in lines:
                if line.split('⋙')[0] == name:
                    editText(f"**Note with the same name already exists**")
                    return
            file = open(f'{path}/message.txt', 'a', encoding='UTF-8', errors='replace')
            try:
                result = ''
                for i in reply.text.split('\n'):
                    result += i + "↹"
                file.write(
                    f'{name}⋙{result[:-1]}⋙"first_name": "{reply.from_user.first_name}", '
                    f'"username": "{reply.from_user.username}", "userid": {reply.from_user.id}, '
                    f'"chat_title": "{reply.chat.title}", "date": "{reply.date}"\n')
                editText(f"**Done!**\nTitle - `{name}`")
            except:
                logging.error("Save text")
            file.close()
            return
        else:
            reply_media = str(reply.media).split('.')[1].lower()

        if reply_media == "photo":
            if os.path.exists(f'{path}/photo/{name}.jpg'):
                editText(f"**File with this name already exists**")
                return
            if set(list(name)) & {'\\', '/', ':', '*', '?', '"', '<', '>', '|'}:
                editText(f"**Forbidden character in title:**\n\ / : * ? \" < > |")
                return

            try:
                if mess[-1] in ["сохр", "сохры", "save"]:
                    name = name.replace(" " + name.split()[-1], "")
                    path1 = f'{save_path}{name}.jpg'
                else:
                    path1 = f'{path}/photo/{name}.jpg'

                app.download_media(reply, file_name=path1)
                editText(f"**Done!**\nTitle - `{name}`")
            except:
                logging.error("Save photo")
        elif reply_media == "voice":
            if os.path.exists(f'{path}/voice/{name}.{reply.voice.mime_type.split("/")[1]}'):
                editText(f"**File with this name already exists**")
                return
            if set(list(name)) & {'\\', '/', ':', '*', '?', '"', '<', '>', '|'}:
                editText(f"**Forbidden character in title:**\n\ / : * ? \" < > |")
                return
            try:
                app.download_media(reply, file_name=f'{path}/voice/{name}.{reply.voice.mime_type.split("/")[1]}')
                editText(f"**Done!**\nTitle - `{name}`")
            except:
                logging.error("Save voice file")
    elif command in commands["vms"]:
        listdir = os.listdir(f'{path}/voice')
        result = ''
        for el in listdir:
            result += f'`{el.split(".")[0]}`\n'
        editText(f"<pre>Your voice messages:</pre>\n{result}")
    elif command in commands["msgs"]:
        read = open(f'{path}/message.txt', 'r', encoding='UTF-8', errors='replace')
        lines = read.readlines()
        read.close()

        result = ''
        for el in lines:
            result += f'`{el.split("⋙")[0]}`\n'
        editText(f"<pre>Your messages:</pre>\n{result}")
    elif command in commands["msg"]:
        read = open(f'{path}/message.txt', 'r', encoding='UTF-8', errors='replace')
        lines = read.readlines()
        read.close()
        name = message.text.split(mess[0].lower())[1][1:]

        author = False
        if mess[-1].lower() in ["author", "ath", "автор", "авт", "from", "user"]:
            author = True

        for el in lines:
            if author:
                if el.split('⋙')[0].split() == name.split()[:-1]:
                    res_dict = loads("{" + el.split('⋙')[2][:-1] + "}")

                    if res_dict['chat_title'] == 'None':
                        res_dict['chat_title'] = 'private'
                    result = f"<pre>Author</pre>\n" \
                             f"**First name:** {res_dict['first_name']}\n" \
                             f"**Username:** [{res_dict['username']}](https://t.me/{res_dict['username']})\n" \
                             f"**User ID:** {res_dict['userid']}\n" \
                             f"**Chat:** {res_dict['chat_title']}\n" \
                             f"**Date:** {res_dict['date'].split()[0]}\n" \
                             f"**Time:** {res_dict['date'].split()[1]}"
            elif el.split('⋙')[0] == name:
                result = ''
                for i in el.split('⋙')[1].split("↹"):
                    result += i + '\n'

            editText(result)
            break
        else:
            editText("**This title is not in the list**")
    elif command in commands["vm"]:
        name = message.text.split(mess[0].lower())[1][1:]
        reply = None
        if message.reply_to_message is not None:
            reply = message.reply_to_message_id

        try:
            app.send_voice(chat_id, f'{path}/voice/{name}.ogg', reply_to_message_id=reply)
            message.delete()
        except:
            editText("**This title is not in the list**")
    elif command in commands["photos"]:
        if mess[-1] in ["сохр", "сохры", "save"]:
            listdir = os.listdir('C:/Сохраненки/фото')
        else:
            listdir = os.listdir(f'{path}/photo')

        result = ''
        for i in listdir:
            result += f'`{i.split(".")[0]}`\n'

        editText(f"<pre>Your photos:</pre>\n{result}")
    elif command in commands["photo"]:
        name = message.text.split(mess[0].lower())[1][1:]
        reply = None
        if message.reply_to_message is not None:
            reply = message.reply_to_message_id

        try:
            app.send_photo(chat_id, f'{path}/photo/{name}.jpg', reply_to_message_id=reply)
            message.delete()
        except ValueError:
            try:
                app.send_photo(chat_id, f'C:/Сохраненки/фото/{name}.jpg', reply_to_message_id=reply)
                message.delete()
            except:
                editText("**This title is not in the list**")
    elif command in commands["delvm"]:
        name = message.text.split(mess[0].lower())[1][1:]

        try:
            os.remove(os.path.join(os.path.abspath(os.path.dirname('C:\\Users\\micro\\PycharmProjects\\'
                                                                   'UserBot_Telegram\\userbot_files\\voice\\')),
                                   f'{name}.ogg'))
            editText(f"**Done!**\nFile < __voice\\{name}.ogg__ > has been deleted")
        except:
            editText("**This title is not in the list**")
    elif command in commands["delphoto"]:
        name = message.text.split(mess[0].lower())[1][1:]

        try:
            os.remove(os.path.join(os.path.abspath(os.path.dirname('C:\\Users\\micro\\PycharmProjects\\'
                                                                   'UserBot_Telegram\\userbot_files\\photo\\')),
                                   f'{name}.jpg'))
            editText(f"**Done!**\nFile < __photo\\{name}.jpg__ > has been deleted")
        except:
            editText("**This title is not in the list**")
    elif command in commands["delmsg"]:
        name = message.text.split(mess[0].lower())[1][1:]
        read = open(f'{path}/message.txt', 'r', encoding='UTF-8', errors='replace')
        lines = read.readlines()
        read.close()

        x = True
        result = ""
        for line in lines:
            if line.split('⋙')[0] != name:
                result += line
            else:
                x = False
        if x:
            editText(f"**No such text in file**")
            return
        write = open(f'{path}/message.txt', 'w', encoding='UTF-8', errors='replace')
        write.write(result)
        write.close()
        editText(f"**Done!**\nText has been removed")
    elif command in commands["spam"]:
        reply = None
        if message.reply_to_message is not None:
            reply = message.reply_to_message_id
        try:
            num = int(mess[1])
            txt = message.text.split(message.text.split()[2] + ' ')[1]
            autodel = False
            message.delete()
        except ValueError:
            try:
                num = int(mess[2])
                if message.text.split()[2] in ['silent', 'бесшумн']:
                    txt = message.text.split(message.text.split()[3] + ' ')[1]
                    autodel = True
                    message.delete()
                else:
                    editText("**Wrong argument**")
                    return
            except:
                editText("**Write number of iterations**")
                return
        except:
            editText("**Write a text for spam**")
            sleep(3)
            message.delete()
            return

        msg_ids = []
        for i in range(num):
            msg = app.send_message(chat_id, txt, reply_to_message_id=reply)
            if autodel:
                msg_ids.append(msg.id)
        for el in msg_ids:
            app.delete_messages(chat_id, el)

        app.send_message(chat_id, "Done!")
    elif command in commands["all_id"]:
        r = message.reply_to_message
        reply = False
        if r is not None:
            reply = True

        result = '<pre>All ID</pre>\n\n' \
                 f'**Your ID** > `{message.from_user.id}`\n'
        if reply:
            result += f'**User Reply ID** > `{r.from_user.id}`\n'

        result += f'**Message ID** > `{message_id}`\n'
        if reply:
            result += f'**Message Reply ID** > `{r.id}`\n'

        if str(message.chat.type).split('.')[1] in ['SUPERGROUP', 'GROUP', 'CHANNEL']:
            result += f'**Chat ID** > `{message.chat.id}`'

        editText(result)
    elif command in commands["logs"]:
        try:
            num = int(mess[1])
        except:
            num = 1

        i = 0
        result = ''
        try:
            for event in app.get_chat_event_log(chat_id):
                if i >= num:
                    break
                action = str(event.action).split(".")[1]
                result += f'<pre>{action.lower()}</pre>'

                if action == "MESSAGE_DELETED":
                    dm = event.deleted_message
                    eu = event.user
                    result += f"\n<a href=\"tg://user?id={eu.id}\">{eu.username}</a> del " \
                              f"<a href=\"tg://user?id={dm.from_user.id}\">message</a> >\n{dm.text}\n"
                elif action == "MESSAGE_EDITED":
                    om = event.old_message
                    result += f"\n__{om.text}__ <a href=\"tg://user?id={om.from_user.id}\">></a>\n{event.new_message.text}\n"
                elif action == "DESCRIPTION_CHANGED":
                    od = event.old_description
                    if od == '':
                        od = "None"
                    result += f"\n__{od}__ <a href=\"tg://user?id={event.user.id}\">></a>\n" \
                              f"{event.new_description}\n"
                elif action == "PHOTO_CHANGED":
                    eu = event.user
                    result += f"\n<a href=\"tg://user?id={eu.id}\">{eu.username}</a> changed group photo\n"
                elif action == "TITLE_CHANGED":
                    result += f"\n__{event.old_title}__ <a href=\"tg://user?id={event.user.id}\">></a>\n{event.new_title}\n"
                elif action == "MEMBER_INVITED":
                    im = event.invited_member
                    eu = event.user
                    result += f"\n<a href=\"tg://user?id={eu.id}\">{eu.username}</a>\n" \
                              f"invited <a href=\"tg://user?id={im.user.id}\">{im.user.username}</a>\n"
                elif action in ["MEMBER_JOINED", "MEMBER_LEFT"]:
                    if action == "MEMBER_LEFT":
                        join_or_left = "left"
                    else:
                        join_or_left = "joined"
                    eu = event.user
                    result += f"\n<a href=\"tg://user?id={eu.id}\">{eu.username}</a> __{join_or_left}__\n"
                elif action in ["ADMINISTRATOR_PRIVILEGES_CHANGED", "MEMBER_PERMISSIONS_CHANGED"]:
                    eu = event.user
                    oap = event.old_administrator_privileges
                    nap = event.new_administrator_privileges
                    if action == "MEMBER_PERMISSIONS_CHANGED":
                        adm_or_member = 'member'
                    else:
                        adm_or_member = 'admin'
                    result += f"\n<a href=\"tg://user?id={eu.id}\">{eu.username}</a> {adm_or_member} change privileges " \
                              f"<a href=\"tg://user?id={oap.user.id}\">{oap.user.username}</a> >\n"

                    res_dict_oap = loads(str(oap.privileges))
                    res_dict_nap = loads(str(nap.privileges))
                    res = []
                    for el in res_dict_nap:
                        if res_dict_oap[el] != res_dict_nap[el]:
                            res.append([el, res_dict_nap[el]])
                    print(res)
                    for el in res:
                        x = '-'
                        if el[1]:
                            x = '+'
                        result += f"__{x}{el[0]}__\n"
                elif action == "SLOW_MODE_CHANGED":
                    result += f"\n__{event.old_slow_mode}__ <a href=\"tg://user?id={event.user.id}\">></a>\n{event.new_slow_mode}\n"
                elif action in ["MESSAGE_PINNED", "MESSAGE_UNPINNED"]:
                    if action == "MESSAGE_PINNED":
                        pin = "pin"
                        pin_id = event.pinned_message.id
                    else:
                        pin = "unpin"
                        pin_id = event.unpinned_message.id
                    eu = event.user
                    result += f"\n<a href=\"tg://user?id={eu.id}\">{eu.username}</a> {pin} " \
                              f"<a href=\"https://t.me/c/{str(chat_id)[3:]}/{pin_id}\">__message link__</a>\n"
                else:
                    result += "__Just Nothing...__"
                i += 1
            try:
                editText(result)
            except:
                editText('**The message text is too long**')
        except:
            editText('**No access to logs**')
    elif command in commands["config"]:
        try:
            command = mess[1].lower()
            new_prefix = str(mess[2:]).replace("'", '"')
            read = open(f'{path}/config.cfg', 'r', encoding='UTF-8', errors='replace')
            lines = read.readlines()
            read.close()
        except:
            text = f'<pre>Config:</pre>\n' \
                   f'**Prefix:**  {cfg["prefix"]}\n' \
                   f'**Prefix Delete:**  {cfg["prefixdel"]}\n' \
                   f'\n<pre>Commands:</pre>\n' \
                   f'**Time**  {commands["time"]}\n' \
                   f'**User:**  {commands["user"]}\n' \
                   f'**Admins:**  {commands["admins"]}\n' \
                   f'**+Message:**  {commands["new_msg"]}\n' \
                   f'**Message:**  {commands["msg"]}\n' \
                   f'**Photo:**  {commands["photo"]}\n' \
                   f'**Voice message:**  {commands["vm"]}\n' \
                   f'**Messages:**  {commands["msgs"]}\n' \
                   f'**Photos:**  {commands["photos"]}\n' \
                   f'**Voice messages:**  {commands["vms"]}\n' \
                   f'**Delete message:**  {commands["delmsg"]}\n' \
                   f'**Delete photo:**  {commands["delphoto"]}\n' \
                   f'**Delete voice message:**  {commands["delvm"]}\n' \
                   f'**Spam:**  {commands["spam"]}\n' \
                   f'**All ids:**  {commands["all_id"]}\n' \
                   f'**Logs:**  {commands["logs"]}\n' \
                   f'**Config:**  {commands["config"]}\n'
            editText(text)
            return

        result = ''
        for line in lines:
            # print(line)
            if command in ["prefix", "префикс"] and line.split(':')[0] == '"prefix"':
                result += f'"prefix": {new_prefix},\n'
                editText(f"**Done!**\nNew prefix: {new_prefix}")
            elif command in ["prefixdel", "префиксдел"] and line.split(':')[0] == '"prefixdel"':
                result += f'"prefixdel": {new_prefix},\n'
                editText(f"**Done!**\nNew delete prefix: {new_prefix}")
            elif command in ["commands", "команды"]:
                try:
                    local_command = mess[2]
                except:
                    logging.error("local_command = mess[2]")
                    editText("**Error**")
                    return

                def check(commandx):
                    if local_command in commands[f"{commandx}"] and line.split(':')[0] == f'    "{commandx}"':
                        new_prefix = str(mess[3:]).replace("'", '"')
                        txt = f'    "{commandx}": {new_prefix},\n'
                        return txt

                all_commands = ["time", "user", "admins", "new_msg", "vms", "msgs", "msg", "vm", "photos", "photo",
                                "delvm", "delphoto", "delmsg", "spam", "all_id", "logs", "config"]
                for el in all_commands:
                    try:
                        result += check(f"{el}")
                        break
                    except:
                        pass
                else:
                    result += line

            else:
                result += line

        write = open(f'{path}/config.cfg', 'w', encoding='UTF-8', errors='replace')
        write.write(result)
        write.close()


if __name__ == "__main__":
    print("logged up")
    app.run()
