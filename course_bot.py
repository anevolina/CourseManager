import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

import button_steps
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
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.callback_answer))
        pass

    def get_tlgr_token(self):
        return os.getenv(f"TELEGRAM_BOT_TOKEN_{self._id}")

    def get_user_id(self, update):

        user_id = update.effective_user.id

        return user_id

    def start_callback(self, bot, update):
        user_id = self.get_user_id(update)
        existed_user = db_module.get_entry(settings.UsersCollection, user_id)

        if existed_user:
            if self.is_course_started(existed_user):
                msg = self.get_message(msg_id=msg_codes.RESET_CONFIRMATION)
                control_buttons = self.get_inline_buttons(step=button_steps.RESET)

            else:
                self.add_course(user_id)
                msg = self.get_message(msg_id=msg_codes.WELCOME_OLD)+ '\n\n' + self.about
                control_buttons = self.get_inline_buttons(step=button_steps.START_COURSE)

        else:
            self.add_user(user_id)
            msg = self.get_message(msg_id=msg_codes.WELCOME_NEW) + '\n\n' + self.about
            control_buttons = self.get_inline_buttons(step=button_steps.START_COURSE)

        self.send_message(bot, user_id, msg, control_buttons)
        return

    def get_message(self, msg_id):

        lang = self.lang
        message = db_module.get_entry(settings.TranslationCollection, msg_id)
        try:
            result = message[lang]
        except KeyError:
            result = message[settings.DefaultLang]
        return self.parse_text(result)

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

    def reset_course(self, bot, update):

        user_id = self.get_user_id(update=update)

        msg = self.about
        buttons = self.get_inline_buttons(step=button_steps.START_COURSE)
        self.send_message(bot, user_id, msg, buttons )

    def cancel_reset(self, bot, update):
        user_id = self.get_user_id(update=update)
        msg = self.get_message(msg_id=msg_codes.RESET_CANCELED)
        self.send_message(bot, user_id, msg)

    def next_step(self, bot, update, step):

        step = int(step)
        user_id = self.get_user_id(update)
        msg, is_it_last = self.get_next_course_step(step)

        if is_it_last:
            buttons = self.get_inline_buttons(step=button_steps.FINISH_COURSE)
        else:
            buttons = self.get_inline_buttons(step=button_steps.NEXT, step_number=step+1)

        self.send_message(bot, user_id, msg, buttons=buttons)

    def callback_answer(self, bot, update):

        query = update.callback_query

        if query.data == msg_codes.RESET_CONFIRM_BUTTON:
            self.reset_course(bot, update)

        elif query.data == msg_codes.RESET_CANCEL_BUTTON:
            self.cancel_reset(bot, update)

        elif query.data.startswith(msg_codes.NEXT_STEP):
            step = query.data.replace(msg_codes.NEXT_STEP, '')
            self.next_step(bot, update, step)

        elif query.data == msg_codes.FINISH_COURSE:
            self.after_course_callback(bot, update)

    @property
    def about(self):
        return self.parse_text(db_module.get_about(self._id))

    def get_inline_buttons(self, step, step_number=None):

        control_buttons = []

        if step == button_steps.RESET:
            confirm_text = self.get_message(msg_id=msg_codes.RESET_CONFIRM_BUTTON)
            decline_text = self.get_message(msg_id=msg_codes.RESET_CANCEL_BUTTON)
            control_buttons = [InlineKeyboardButton(confirm_text, callback_data=msg_codes.RESET_CONFIRM_BUTTON),
                               InlineKeyboardButton(decline_text, callback_data=msg_codes.RESET_CANCEL_BUTTON)]

        elif step == button_steps.START_COURSE:
            text = self.get_message(msg_id=msg_codes.START_COURSE_BUTTON)
            control_buttons = [InlineKeyboardButton(text, callback_data=msg_codes.NEXT_STEP + '0')]

        elif step == button_steps.NEXT:
            text = self.get_message(msg_id=msg_codes.NEXT_STEP)
            control_buttons = [InlineKeyboardButton(text, callback_data=(msg_codes.NEXT_STEP + str(step_number)))]

        elif step == button_steps.FINISH_COURSE:
            text = self.get_message(msg_id=msg_codes.FINISH_COURSE)
            control_buttons = [InlineKeyboardButton(text, callback_data=msg_codes.FINISH_COURSE)]

        return InlineKeyboardMarkup([control_buttons])

    def send_message(self, bot, user_id, msg, buttons=None):
        bot.send_message(chat_id=user_id, text=msg, reply_markup=buttons)

    def get_next_course_step(self, step):
        next_step, is_it_last_step = db_module.get_next_course_step(self._id, step)
        next_step = self.parse_text(next_step[settings.CourseContentTextField])

        return next_step, is_it_last_step

    def parse_text(self, text):
        return '\n'.join(text.split('\\n'))

    def after_course_callback(self, bot, update):
        user_id = self.get_user_id(update)
        step = db_module.get_next_step(user_id, self._id)

        if step >= 5:
            msg = self.get_message(msg_codes.AFTER_COURSE)
            self.send_message(bot, user_id, msg)
            db_module.reset_user_step(user_id, self._id)
        else:
            db_module.increase_course_step(user_id, self._id)
