class WalletError(Exception):
    pass


class WalletNotFoundError(WalletError):
    pass


class InvalidAmountError(WalletError):
    pass


class InsufficientFundsError(WalletError):
    pass


class WalletBalanceError(WalletError):
    pass


class WalletOperationError(WalletError):
    pass
