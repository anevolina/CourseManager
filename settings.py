from pymongo import MongoClient

#Default mongo & db settings
DefaultMongo = 'mongodb://localhost:27017/'
DefaultDB = 'CourseManager'
DefaultLang = 'EN'

#Collections
CoursesCollection = 'Courses'
TranslationCollection = 'Translation'
UsersCollection = 'Users'

#Fields
IdField = '_id'
CourseTokenField = 'token'
CourseIsPrivateField = 'is_private'
CourseContentField = 'content'

CourseContentTextField = 'text'
CourseLangField = 'language'
CourseAboutField = 'about'

TranslationRuField = 'RU'
UsersExternalIdsField = 'external_id'
UsersCoursesField = 'courses'
UsersCourseIdField = 'course_id'
UsersCourseStepField = 'step'
UserCourseAllowedField = 'allowed'

UploadCollections = [CoursesCollection, TranslationCollection]

DB = None

def connect_database(db: str = DefaultMongo):
    """
    Auxiliary function to get matching database connection
    :return: 'matching' database connection from mongoDB
    """

    global DB

    if not DB:

        mongo_client = MongoClient(db)
        DB = mongo_client[DefaultDB]

    return DB


def get_collection(collection: str, db: str = DefaultMongo):
    """

    :param collection:
    :param db:
    :return:
    """
    db = connect_database(db)
    collection = db.get_collection(collection)

    return collection