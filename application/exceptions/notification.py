class NotificationError(Exception):
    pass


class NotificationUnavailableError(NotificationError):
    pass


class NotificationRejectedError(NotificationError):
    pass


class InvalidNotificationResponseError(NotificationError):
    pass
