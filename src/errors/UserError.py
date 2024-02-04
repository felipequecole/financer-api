class UserError(Exception):

    def __init__(self, message, cause=None, code='-1'):
        super().__init__(message, cause)
        self.message = message
        self.cause = cause
        self.code = code
