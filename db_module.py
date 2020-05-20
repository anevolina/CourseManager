import exceptions
import settings


def get_token(course_id: str):
    param = {settings.IdField: {'$eq': course_id}}

    entry = get_all_entries(settings.CoursesCollection, param, {settings.CourseTokenField: 1})

    assert entry, f"Course with id: {course_id} not found!"

    return entry[0][settings.CourseTokenField]


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


def reset_user_progress(user_id, course_id):
    param, step_field = get_param_and_step_field(user_id, course_id)
    set_new_value_to_field(settings.UsersCollection, param, step_field, 0)


def get_entry(collection, _id):

    collection = settings.get_collection(collection)
    param = {settings.IdField: {'$eq': _id}}

    return collection.find_one(param)


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


def get_next_course_step(user_id, course_id):
    step = get_next_step(user_id, course_id)
    collection = settings.get_collection(settings.CoursesCollection)
    res = collection.find_one(
        {settings.IdField: course_id},
        {settings.IdField: 0, settings.CourseContentField: 1}
    )

    return res[settings.CourseContentField][step]


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