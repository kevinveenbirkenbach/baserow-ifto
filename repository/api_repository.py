class ApiRepository:
    def __init__(self, api, verbose=False):
        self.api = api
        self.verbose = verbose

    def print_verbose_message(self, message):
        if self.verbose:
            print(message)