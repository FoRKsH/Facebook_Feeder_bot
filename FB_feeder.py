from FB_Page import *
import Global
import random
import telepot

from telepot import glance
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open, per_callback_query_chat_id
from telepot.namedtuple import InputMediaPhoto as InputPhoto, InputMediaVideo as InputVideo
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton



class FaceFeeder(telepot.helper.ChatHandler):

    def __init__(self, *args, **kwargs):
        super(FaceFeeder, self).__init__(*args, **kwargs)
        self.not_active = True
        self.chat_ID = None
        self.pages = []
        self.state = "Command"
        self.auto_timer = random.randrange(1800, 28800, 450)
        self.inline_message = None
        self.event = None
        self.automatic_update = True
        self.router.routing_table['_alarm'] = self.auto_check
        self.event = self.scheduler.event_later(self.auto_timer, ('_alarm', {'payload': self.auto_timer}))

    def back_keyboard(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="back", callback_data="/Back")]], )
        return keyboard

    def menu_keyboard(self):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="View List", callback_data="/List"),
             InlineKeyboardButton(text="Help", callback_data="/Help")],
            [InlineKeyboardButton(text="Subscribe", callback_data="/Subscribe"),
             InlineKeyboardButton(text="Unsubscribe", callback_data="/Unsubscribe")],
            [InlineKeyboardButton(text="Auto Update : " + ("ON" if self.automatic_update else "OFF"),
                                  callback_data="/Automatic")],
            [InlineKeyboardButton(text="DONATE AND SUPPORT", callback_data="/Donate")]], )

        return keyboard

    def admin_keyboard(self):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="SHUTDOWN SYSTEM !!", callback_data="/Shutdown")],
            [InlineKeyboardButton(text="Broadcast Message", callback_data="/Message")],
            [InlineKeyboardButton(text="Admin Backup", callback_data="/Backup")],
            [InlineKeyboardButton(text="Number of Users", callback_data="/USER_COUNT")],
            [InlineKeyboardButton(text="Back", callback_data="/Back")]
        ], )
        return keyboard

    def auto_check(self, event):
        if self.automatic_update is True:
            if len(self.pages) > 0:
                for page in self.pages:
                    try:
                        self.sending_posts(page)
                    except (telepot.exception.BotWasBlockedError, telepot.exception.BotWasKickedError):
                        Global.log("\nBlocked User")
                        if self.id in Global.user_profiles:
                            del Global.user_profiles[str(self.id)]
                        try:
                            self.scheduler.cancel(self.event)
                        except:
                            pass

                    except Exception as e:
                        Global.log(e)
            self.auto_timer = 28800  # update every 8 hours , avoid 'I am not robot test'
            self.event = self.scheduler.event_later(self.auto_timer, ('_alarm', {'payload': self.auto_timer}))

    def on_chat_message(self, msg):
        if self.not_active:
            self.not_active = False
            self.chat_ID = msg['chat']['id']

            if self.chat_ID == Global.admin_id:
                try:
                    self.scheduler.cancel(self.event)
                except:
                    pass
                finally:
                    self.auto_timer = 30
                    self.event = self.scheduler.event_later(self.auto_timer, ('_alarm', {'payload': self.auto_timer}))

            if str(self.chat_ID) in Global.user_profiles:  # user already exist
                self.pages = Global.user_profiles[str(self.chat_ID)][:]
                return
            else:  # new user account
                Global.user_profiles[str(self.chat_ID)] = self.pages[:]

        self.inline_message = None

        try:
            self.handle_message(msg['text'])
        except (telepot.exception.BotWasBlockedError, telepot.exception.BotWasKickedError):
            Global.log("\nBlocked User")
            if self.id in Global.user_profiles:
                del Global.user_profiles[str(self.id)]
            try:
                self.scheduler.cancel(self.event)
            except:
                pass
        except Exception as e:
            Global.log(e)
            pass

    def on_callback_query(self, msg):
        query_id, from_id, command = glance(msg, flavor='callback_query')
        Global.bot.answerCallbackQuery(query_id)

        try:
            self.handle_message(msg['data'])
        except (telepot.exception.BotWasBlockedError, telepot.exception.BotWasKickedError):
            Global.log("\nBlocked User")
            if self.id in Global.user_profiles:
                del Global.user_profiles[str(self.id)]
            try:
                self.scheduler.cancel(self.event)
            except:
                pass
        except:
            pass

    def on__idle(self, event):
        pass

    def sending_posts(self, page):
        try:
            posts = page.get_new_posts()
        except Exception as e:
            Global.log(e)
            # self.sender.sendMessage("this page was deleted by admin : " + page.name)
            # self.sender.sendMessage("removed automatically")
            # self.remove_page(page)
            return
        if len(posts) > 0:
            if self.chat_ID > 0:  # user id
                self.sender.sendMessage("Posts From : " + page.name)
            for post in reversed(posts):
                page.load_next(post)
                album = []
                ###       Text part
                if len(page.text) > 0:
                    if (len(page.text) < 4096):
                        self.sender.sendMessage(page.text, disable_web_page_preview=True)
                    else:
                        for x in range(0, len(page.text), 4096):  # telegram max message length is 4096 char
                            self.sender.sendMessage(page.text[x:x + 4096], disable_web_page_preview=True)
                #################################################

                ###        Image part
                if page.images is not None:
                    for image in page.images:
                        album.append(InputPhoto(media=image))
                #################################################

                ###       Video part
                if page.video is not None:
                    album.append(InputVideo(media=page.video))
                #################################################

                ### Sending the album
                if len(album) != 0:
                    self.sender.sendMediaGroup(album)
                #######################################################

        self.inline_message = None
        page.delete_cached_post()

    def send_safe_message(self, msg, kb):
        if self.inline_message is not None:
            edited_message_id = telepot.message_identifier(self.inline_message)
            try:
                Global.bot.editMessageText(edited_message_id, msg, reply_markup=kb)
            except:
                self.inline_message = self.sender.sendMessage(msg, reply_markup=kb)
        else:
            self.inline_message = self.sender.sendMessage(msg, reply_markup=kb)

    def page_not_found(self, FBPage):
        try:
            FBPage.get_new_posts()
            FBPage.reset_page()
            return False
        except Exception as e:
            Global.log(str(e))
            return True

    def remove_page(self, page):
        self.pages.remove(page)
        Global.user_profiles[str(self.chat_ID)] = self.pages[:]

    def handle_message(self, msg):
        command = msg

        if command.title() == "/Back":
            message = "How May I help"
            self.send_safe_message(message, self.menu_keyboard())
            self.state = "Command"
            return

        elif self.state == "ADMIN":

            if command == "/Shutdown":
                message = "System will be shutdown in 1 minutes"
                Global.commandor = "Shutdown"
                self.send_safe_message(message, self.back_keyboard())
                self.state = "Command"

            elif command == "/Message":
                message = "Broadcast message to all users\n Enter your message and hit send"
                self.send_safe_message(message, self.back_keyboard())
                self.state = "ADMIN_MSG"

            elif command == "/Backup":
                message = "Admin Backup will be ready in seconds"
                Global.commandor = "Admin_Backup"
                self.send_safe_message(message, self.back_keyboard())
                self.state = "Command"

            elif command == "/USER_COUNT":
                message = "Number of users : " + str(len(Global.user_profiles))
                self.send_safe_message(message, self.back_keyboard())

            else:
                self.inline_message = self.sender.sendMessage('Invalid Admin Command',
                                                              reply_markup=self.menu_keyboard())
                self.state = "Command"

        elif self.state == "ADMIN_MSG":
            Global.admin_msg = msg
            Global.commandor = "Msg"
            self.state = "Command"
            message = "Will be Broadcasted soon to all"
            self.inline_message = self.sender.sendMessage(message, reply_markup=self.menu_keyboard())

        elif command.title() in ["/Menu", "Menu", "/Start", "Start"]:
            self.inline_message = self.sender.sendMessage('How May I help', reply_markup=self.menu_keyboard())
            self.state = "Command"

        elif command.title() in ["/Help", "Help"]:
            message = "Use List to view your subscribed list\n\n"
            message += "Use Subscribe to add new page\n\n"
            message += "Use Unsubscribe to remove page\n\n"
            message += "Use Automatic to enable disable auto check for new posts every hour\nDefault is ON\n\n"
            message += "Use Help to .....  are u kidding !!\n\n"

            self.send_safe_message(message, self.back_keyboard())

            self.state = "Command"

        elif command.title() == "/List":
            if len(self.pages) == 0:
                message = "Your list is empty , use Subscribe to add some "
                self.send_safe_message(message, self.back_keyboard())

            else:
                message = ""
                for page in self.pages:
                    message += page.name + "\n"

                self.send_safe_message(message, self.back_keyboard())

            self.state = "Command"

        elif command.title() == "/Admin":
            if self.chat_ID == Global.admin_id:
                self.state = "ADMIN"
                message = "Welcome to Admin Panel"
                self.inline_message = self.sender.sendMessage(message, reply_markup=self.admin_keyboard())

            else:
                message = 'Enter a Valid Command\n'
                self.inline_message = self.sender.sendMessage(message, reply_markup=self.menu_keyboard())

        elif self.state == "Command":

            if command.title() == "/Subscribe":
                message = "Enter tag name of page you want to subscribe to"
                if len(self.pages) == 0:
                    try:
                        self.sender.sendPhoto(open("Help.png", "rb"))
                    except Exception as e:
                        Global.log(e)
                self.inline_message = self.sender.sendMessage(message, reply_markup=self.back_keyboard())

                self.state = "Subscribe"

            elif command.title() == "/Unsubscribe":

                if len(self.pages) == 0:
                    message = "Your list is Empty"
                    self.send_safe_message(message, self.back_keyboard())

                else:
                    message = "Enter name of page you want to Unsubscribe to"
                    self.send_safe_message(message, self.back_keyboard())
                    self.state = "UnSubscribe"

            elif command.title() == "/Automatic":

                if self.automatic_update is True:
                    self.automatic_update = False
                    message = "Automatic Update : OFF"
                    self.send_safe_message(message, self.menu_keyboard())

                    try:
                        self.scheduler.cancel(self.event)
                        for page in self.pages:
                            page.reset_page()
                    except:
                        pass
                else:
                    self.automatic_update = True
                    message = "Automatic Update : ON"
                    self.send_safe_message(message, self.menu_keyboard())
                    self.event = self.scheduler.event_later(self.auto_timer, ('_alarm', {'payload': self.auto_timer}))

            elif command.title() == "/Donate":
                if self.inline_message:
                    edited_message_id = telepot.message_identifier(self.inline_message)

                message = "Donation is needed for hosting\nthe bot on the server\n"
                message += "Donate using Paypal : "
                message += "paypal.me/FoRKsH\n"
                message += "Donate using Bitcoin\n"
                message += "\n`1BADfU3ZJosVF4pQRCwMGCk3hrMxefWQZX`\n"
                message += "\nany amount will be appreciated."

                if self.inline_message:
                    Global.bot.editMessageText(edited_message_id,
                                               message,
                                               disable_web_page_preview=True,
                                               parse_mode='Markdown',
                                               reply_markup=self.back_keyboard())
                else:
                    self.inline_message = self.sender.sendMessage(message,
                                                                  disable_web_page_preview=True,
                                                                  parse_mode='Markdown',
                                                                  reply_markup=self.back_keyboard())

            elif command[0] == "/":
                message = 'Enter a Valid Command\n'
                message += 'Or say "help" if get lost'
                self.inline_message = self.sender.sendMessage(message, reply_markup=self.menu_keyboard())
            else:
                self.inline_message = None

        elif self.state == "Subscribe":

            if command[0] == "/":
                message = 'Enter a Valid Command\n'
                message += 'Or say "help" if get lost'
                self.inline_message = self.sender.sendMessage(message, reply_markup=self.back_keyboard())
                return

            if len(self.pages) != 0:
                for page in self.pages:
                    if command == page.name:
                        self.inline_message = self.sender.sendMessage(
                            "page : " + command + " is already in your subscribed list",
                            reply_markup=self.menu_keyboard())
                        self.state = "Command"
                        return

            FBPage = FB_page(command)  # command here is the facebook page name the user will send

            if self.page_not_found(FBPage):
                self.sender.sendMessage("PAGE TAG : " + FBPage.name + " NOT FOUND", reply_markup=self.back_keyboard())
                self.state = "Command"
                return

            message = "page : " + command + " added to your subscribed list\n"

            if self.chat_ID > 0:
                message += "Getting Last post from " + command

            self.sender.sendMessage(message)

            self.pages.append(FBPage)
            Global.user_profiles[str(self.chat_ID)] = self.pages[:]
            self.sending_posts(FBPage)
            self.inline_message = None
            self.state = "Command"

        elif self.state == "UnSubscribe":

            if len(self.pages) != 0:
                for page in self.pages:
                    if command == page.name:
                        self.remove_page(page)
                        self.inline_message = self.sender.sendMessage(
                            "page : " + command + " had been removed from subscribed list",
                            reply_markup=self.back_keyboard())

                        self.state = "Command"
                        return
                self.inline_message = self.sender.sendMessage("page : " + command + " wasn't in your subscribed list",
                                                              reply_markup=self.back_keyboard())

            self.state = "Command"
