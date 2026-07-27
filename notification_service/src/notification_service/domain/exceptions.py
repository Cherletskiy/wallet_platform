class NotificationError(Exception):
    pass


class InvalidNotificationAmountError(NotificationError):
    pass


class NotificationProcessingError(NotificationError):
    pass
