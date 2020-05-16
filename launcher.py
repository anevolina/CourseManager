import db_module
from sbs_course import StepByStepCourse

all_bots = db_module.get_bots_ids()

started_bots = []
for each in all_bots:
    new_bot = StepByStepCourse(each)
    new_bot.start_bot()
    started_bots.append(new_bot)

