from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

import db_module
import msg_codes
import settings

class CourseBot:
    def __init__(self, _id: str):
        self._id = _id
        self.lang = db_module.get_course_language(_id)
        self.updater = None
        self.commands = {}

    def start_bot(self):
        tlgr_token = self.get_tlgr_token()
        self.updater = Updater(token=tlgr_token)
        self.get_commands()
        self.add_command_handlers()
        self.add_other_handlers()
        self.updater.start_polling()

    def get_commands(self):
        all_functions = [f for f in dir(self) if f.endswith('_callback')]
        for each in all_functions:
            key = each.replace('_callback', '')
            self.commands[key] = each

    def add_command_handlers(self):
        for k, v in self.commands.items():
            self.updater.dispatcher.add_handler(CommandHandler(k, self.__getattribute__(v)))

    def add_other_handlers(self):
        pass

    def get_tlgr_token(self):

        return db_module.get_token(self._id)

    def get_user_id(self, update):
        return update.message.from_user.id

    def start_callback(self, bot, update):

        user_id = self.get_user_id(update)
        existed_user = db_module.get_entry(settings.UsersCollection, user_id)

        if existed_user:
            if self.is_course_started(existed_user):
                msg = self.get_message(msg_id=msg_codes.RESET_CONFIRMATION)
                #TODO add inline buttons

            else:
                self.add_course(user_id)
                msg = self.get_message(msg_id=msg_codes.WELCOME_OLD)

        else:
            self.add_user(user_id)
            msg = self.get_message(msg_id=msg_codes.WELCOME_NEW)

        db_module.reset_user_progress(user_id, self._id)
        bot.send_message(chat_id=user_id, text=msg)
        return

    def handle_user_message(self, bot, update):
        print('I was here')

    def get_message(self, msg_id):

        lang = self.lang
        message = db_module.get_entry(settings.TranslationCollection, msg_id)
        try:
            result = message[lang]
        except KeyError:
            result = message[settings.DefaultLang]
        return result

    def add_user(self, user_id):
        db_module.add_user(user_id, self._id)
        pass

    def add_course(self, user_id):
        db_module.add_course(user_id, self._id)
        pass

    def is_course_started(self, user: dict):
        course_started = False

        for course in user[settings.UsersCoursesField]:
            if course[settings.UsersCourseIdField] == self._id:
                course_started = True
                break

        return course_started


test = CourseBot('ololo')
test.start_bot()

print(test.get_message('welcome_new'))