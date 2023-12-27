
class NotFoundInApplicationException(Exception):
    def __init__(self, message="This is a custom exception."):
        super().__init__(f"Not found in application: {message}")


class MissingConfigException(Exception):
    def __init__(self, message="This is a custom exception."):
        super().__init__(f"Missing config: {message}")


class NothingFoundInConfigException(Exception):
    def __init__(self, message="This is a custom exception."):
        super().__init__(f"Nothing found in config for : {message}")