class NoDialogFoundException(Exception):
    """Exception for when trying to access dialog when none is found."""

    def __init__(self, speaker=None, message=None):
        """Initialize with appropriate message."""
        if speaker is None:
            message = 'No dialog found.'
        else:
            message = 'Speaker "{}" has no known dialog.'.format(speaker)
        super(NoDialogFoundException, self).__init__(message)
        self.speaker = speaker
