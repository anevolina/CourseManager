import db_module
from sbs_course import StepByStepCourse

all_bots = db_module.get_bots_ids()

started_bots = []
for bot_id in all_bots:
    new_bot = StepByStepCourse(bot_id)
    new_bot.start_bot()
    print(f"Bot '{bot_id}' started")
    started_bots.append(new_bot)
