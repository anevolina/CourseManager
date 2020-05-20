class CourseManagerException(Exception):
    """Base exception"""
    pass


class CourseNotFoundException(CourseManagerException):
    pass

