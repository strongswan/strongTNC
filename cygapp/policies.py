from models import Policy

class FileHash(Policy):
    """ Policy to check if a given file hash matches its reference value. """
    type = 1

class DirHash(Policy):
    """ Policy to check if all files in a given directory match their
    respective reference value. """
    type = 2

class ListeningPort(Policy):
    """ Policy to check wheter there is a listening port in a given port range.
    """
    type = 3

    def __init__(self, lower = 1, upper = 65536):
        if lower > upper or lower < 1 or upper > 65536:
            raise ValueError('Invalid port range')
        self.lower = lower
        self.upper = upper
    
    def __unicode__(self):
        return 'from %d to %d' % (self.lower, self.upper)

class FileExist(Policy):
    """ Policy to check if a given file exists. """
    type = 4

    def __init__(self, file, **kwargs):
        kwargs['type'] = FileExist.type
        self.argument = '%d' % file.id

class NotFileExist(Policy):
    """ Policy to check if a given file does not exist. """
    type = 5

class MissingUpdate(Policy):
    """ Policy to check if any package updates are missing. """
    type = 6

class MissingSecurityUpdate(Policy):
    """ Policy to check if any security-relevant udpates are missing. """
    type = 7

class Blacklist(Policy):
    """ Policy to check if any blacklisted packages are installed. """
    type = 8

class OSSettings(Policy):
    """ Policy that reads OS Settings. """
    type = 9

class Deny(Policy):
    """ Policy that fails always per definition. """
    type = 10

