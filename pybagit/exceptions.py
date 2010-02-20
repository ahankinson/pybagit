""" Exceptions for PyBagIt """

class BagError(Exception):
    """ BagIt Errors """
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return repr(self.message)
        
class BagDoesNotExistError(BagError): pass
class BagIsNotValidError(BagError): pass
class BagCouldNotBeCreatedError(BagError): pass
class BagFormatNotRecognized(BagError): pass
class BagCheckSumNotValid(BagError): pass
class BagFileDownloadError(BagError): pass