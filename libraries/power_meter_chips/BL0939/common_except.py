#return is ok
RETURN_OK = 0

class CustomError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)
        self.errorinfo=ErrorInfo

    def __str__(self):
        return self.errorinfo

def error_put(value, str):
    if value != RETURN_OK:
        raise CustomError(str)