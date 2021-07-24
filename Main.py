# BOT V 0.3.3 #
import os
import time
from Save_Data import *
from FB_feeder import *


def broadcast_message(msg):
    for profile in Global.user_profiles:
        try:
            if int(profile) > 0:
                Global.bot.sendMessage(profile, "Message form ADMIN\n\n" + msg)
        except Exception as e:
            Global.log(e)
            pass

def shutdown_system():
    os._exit(1)

def Read_Admin_Panel():
    if Global.commandor == "Shutdown":
        Global.going_to_shutdown = True

    elif Global.commandor == "Msg":
        if Global.admin_msg is not None:
            broadcast_message(Global.admin_msg)
            Global.admin_msg = None

    elif Global.commandor == "Admin_Backup":
        admin_backup(Global.user_profiles)
        Global.bot.sendMessage(Global.admin_id, "Admin Backup is ready")
        try:
            Global.bot.sendDocument(Global.admin_id,document = open("Database/Admin_Backup.db","rb"))
        except Exception as e:
            Global.log(e)
            Global.bot.sendMessage(Global.admin_id, "Error sending The Backup !")

    Global.commandor = None

def dummy_msg(id, Type):
    message_id = 0
    frm = {'id': id, 'is_bot': False, 'first_name': "x", 'last_name': "x", 'username': "x", 'language_code': 'en'}
    chat = {'id': id, 'first_name': "x", 'last_name': "x", 'username': "x", 'type': Type}
    date = 0
    text = "/Loading"
    entities = [{'offset': 1, 'length': 8, 'type': 'bot_command'}]

    msg = {'message_id': message_id, 'from': frm, 'chat': chat, 'date': date, 'text': text, 'entities': entities}
    return msg

def Restore_Users_Sessions():
    for profile in Global.user_profiles:
        try:
            if int(profile) > 0:
                Global.bot.handle(dummy_msg(int(profile), 'private'))
            elif int(profile) < 0:
                Global.bot.handle(dummy_msg(int(profile), 'channel'))
        except:
            pass

def Create_Important_Directory():
    if not os.path.exists("Database"):
        os.mkdir("Database")

    if not os.path.exists("Debugging"):
        os.mkdir("Debugging")




Global.bot_token = input("Token : ")
Global.admin_id = input("Admin ID :")

Create_Important_Directory()

Global.log("\n\n*********************" + str(time.strftime("%Y/%m/%d %I%p", time.localtime()))+"*********************")

Global.user_profiles = load_profiles()

Global.bot = telepot.DelegatorBot(Global.bot_token, [
    pave_event_space()([per_chat_id(), per_callback_query_chat_id()], create_open, FaceFeeder, timeout=1,
                       include_callback_query=True),
])
Restore_Users_Sessions()

MessageLoop(Global.bot).run_as_thread()
print("Started...")
hour_counter = 0

while (1):

    time.sleep(9)  # sleep for 9 second avoid high useless process , schuldue some events
    hour_counter += 0.0025
    Read_Admin_Panel()

    if Global.going_to_shutdown:
        time.sleep(60)
        save_profiles(Global.user_profiles)
        print("Power OFF!")
        shutdown_system()

    if (hour_counter >= 4):  # Create Backup every 4 hours
        save_profiles(Global.user_profiles)
        hour_counter = 0


