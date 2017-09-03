class NoDialogFoundException(Exception):
    """Exception for when trying to access dialog when none is found."""

    def __init__(self, message=None):
        """Initialize with appropriate message."""
        if not message:
            message = 'No dialog found.'
        super(NoDialogFoundException, self).__init__(message)


class SpeakerNotFoundException(NoDialogFoundException):
    """Exception for when trying to access dialog for a speaker who has none."""

    def __init__(self, speaker):
        """Initialize with appropriate message."""
        message = 'Speaker "{}" has no known dialog.'.format(speaker)
        super(SpeakerNotFoundException, self).__init__(message)
        self.speaker = speaker
