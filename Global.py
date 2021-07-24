user_profiles = None
bot = None

#Admin part
admin_msg = None
commandor = None
going_to_shutdown = False

#Settings part will be added using console soon
admin_id = ""
bot_token = ""      #From Command Line

#Debugging Part
def log(txt):
    with open("Debugging/log.txt", "a") as file:
        file.write(str(txt) + "\n")