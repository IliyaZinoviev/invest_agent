class ExternalMarketError(Exception):
    def __init__(self, msg, detail, code, ticker):
        self.msg = msg
        self.detail = detail
        self.code = code
        self.ticker = ticker
        super().__init__(msg)
