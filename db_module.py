import exceptions
import settings


def get_bots_ids():
    return [b[settings.IdField] for b in get_all_entries(settings.CoursesCollection, {}, {settings.IdField: 1})]


def get_all_entries(collection: str, parameters: dict, fields: dict = None):

    coll = settings.get_collection(collection)

    if not fields:
        result = list(coll.find(parameters))

    else:
        result = list(coll.find(parameters, fields))

    return result


def get_course_language(course_id):
    course_entry = get_entry(settings.CoursesCollection, course_id)

    return course_entry[settings.CourseLangField]


def set_new_value_to_field(collection: str, param: dict, field: str, value):

    collection = settings.get_collection(collection)
    collection.update_one(param, {'$set': {field: value}})

    pass


def reset_user_step(user_id, course_id):
    param, step_field = get_param_and_step_field(user_id, course_id)
    set_new_value_to_field(settings.UsersCollection, param, step_field, 0)


def get_entry(collection, _id):

    collection = settings.get_collection(collection)
    param = {settings.IdField: {'$eq': _id}}

    return collection.find_one(param)

def find_one(collection, search: dict, param: dict):
    collection = settings.get_collection(collection)
    return collection.find_one(search, param)


def add_user(user_id, course_id):
    users_collection = settings.get_collection(settings.UsersCollection)
    users_collection.insert({settings.IdField: user_id})
    add_course(user_id, course_id)


def add_course(user_id, course_id):
    course_data = [
        {
            settings.UsersCourseIdField: course_id,
            settings.UsersCourseStepField: 0,
            settings.UserCourseAllowedField: True
        }
    ]
    update_array_field(settings.UsersCollection, user_id, settings.UsersCoursesField, course_data)


def update_array_field(collection: str, _id, field: str, value: list):

    collection = settings.get_collection(collection)
    collection.update_one({settings.IdField: _id}, {'$addToSet': {field: {'$each': value}}}, True)

    pass


def get_next_course_step(course_id, step):
    search = {settings.IdField: course_id}
    param = {settings.IdField: 0, settings.CourseContentField: 1}
    res = find_one(settings.CoursesCollection, search, param)

    length = len(res[settings.CourseContentField])
    last_step = (length - 1 <= step)

    return res[settings.CourseContentField][step], last_step


def increase_course_step(user_id, course_id):
    course_position, step_field = get_param_and_step_field(user_id, course_id)
    increment_field(settings.UsersCollection, course_position, step_field, 1)
    pass


def increment_field(collection, param, field, value):
    """
    Increment exact field by value
    """

    collection = settings.get_collection(collection)
    collection.update_one(param, {'$inc': {field: value}}, upsert=True)

    return


def get_param_and_step_field(user_id, course_id):
    course_field = settings.UsersCoursesField + '.' + settings.UsersCourseIdField
    step_field = settings.UsersCoursesField + '.$.' + settings.UsersCourseStepField
    param = {settings.IdField: user_id, course_field: course_id}

    return param, step_field


def get_next_step(user_id, course_id):

    collection = settings.get_collection(settings.UsersCollection)
    res = collection.find_one(
        {settings.IdField: user_id},
        {
            settings.IdField: 0,
            settings.UsersCoursesField: {'$elemMatch': {settings.UsersCourseIdField: course_id}}
        }
    )

    if res:
        return res[settings.UsersCoursesField][0][settings.UsersCourseStepField]

    else:
        raise exceptions.CourseNotFoundException(f"user: {user_id} doesn't have this course '{course_id}'")


def get_about(course_id):
    search = {settings.IdField: course_id}
    param = {settings.IdField: 0, settings.CourseAboutField: 1}
    return find_one(settings.CoursesCollection, search, param)[settings.CourseAboutField]


def insert_entries(colleciton_name, entries):

    colleciton = settings.get_collection(colleciton_name)
    failed = []
    for entry in entries:
        try:
            colleciton.update({settings.IdField: entry[settings.IdField]}, entry, upsert=True)
        except Exception as e:
            failed.append(f'{entry}: {e}')

    if failed:
        failed = '\n'.join(failed)
        raise Exception(f"\nCollection {colleciton_name.upper()} failed to update entries:\n{failed}")
