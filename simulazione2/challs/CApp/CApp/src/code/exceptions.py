from flask import current_app

class CappExcpetion(Exception):
    def __str__(self):
        if current_app.config['DEBUG']:
            print(self.args)
        return 'Error'
        
class NotLogged(CappExcpetion):
    pass

class WrongPassword(CappExcpetion):
    pass

class EnvarNameTooBig(CappExcpetion):
    def __str__(self):
        base = super().__str__()
        return base + ': Envar name too big.'

class EnvarValueTooBig(CappExcpetion):
    def __str__(self):
        base = super().__str__()
        return base + ': Envar value too big.'

class TooManyEnvars(CappExcpetion):
    def __str__(self):
        base = super().__str__()
        return base + ': Too many envars.'

class EnvarNotFound(CappExcpetion):
    def __str__(self):
        super().__str__()
        return ''

class FileTooBig(CappExcpetion):
    def __str__(self):
        super().__str__()
        return 'File too big. Max file size:' + str(current_app.config['max_file_size'])

class VMNotFound(CappExcpetion):
    pass