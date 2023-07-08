

from .helpers import *
import sys
import os
from flask import current_app
import glob
import base64 
import traceback

# CCOs Kernel
class WM(object):
    def __init__(self, owner) -> None:
        self.env_vars = {}
        self.owner = owner
        try:
            self.vm_id = self.load(owner)
        except VMNotFound:
            self.vm_id = self.initialize(owner)
            self.env_vars = {'VM_ID': self.vm_id}
        self.root_dir = f'/opt/volumes/volume-{self.vm_id}/'

    # Execute a single statement
    def execute_statement(self, line:str):
        line = line.strip() 
        if line=='':
            return ''
        

        args = [l.strip() for l in line.split(' ') if l != ''] # Arguments of an instruction
        cmd = args.pop(0)                                      # Instruction

        args = self.replace_vars(args)
        cmd, args = self.check_security(cmd, args)

        return self.execute_ins(cmd, args)

    def check_security(self, cmd, args):
        # Allowed instruction
        self.allowlist = ['ls', 'cat', 'write', 'echo', 
                          'get_envar', 'set_envar', 'del_envar', 
                          'help', 'eval_expr', 'base64e', 'base64d', 
                          'mkdir', 'uname']
        # For security, delete the following sequence of characters.
        # Add your own for improved security! (Note to player: the checker is pretty strict.....)
        blocklist = ["subprocess", '..', "\n", "union", "__import__"]

        if cmd not in self.allowlist:
            return 'invalid_ins', cmd
        
        safe_args = []
        for arg in args:
            new_arg = arg
            for blocked in blocklist:
                new_arg = new_arg.replace(blocked, '')
            safe_args.append(new_arg)
        
        return cmd, safe_args

    # Replace the env_vars inside an argument of an instruction
    def replace_vars(self, args):
        new_args = []
        for arg in args:
            try:
                new_args.append(arg.format(**self.env_vars))
            except:
                pass
        return new_args

    # Command not found
    def invalid_ins(self, command_name):
        return command_name + ': Command not found.'
    
    # Execute the actual instruction
    def execute_ins(self, cmd, args):
        ins = self.__getattribute__(cmd)
        return ins(args)

    def echo(self, args):
        return ' '.join(args)

    # File operations

    def ls(self, args):
        if len(args)<1:
            path = ''
        else:
            path = args[0]
        files = [f.split('/')[-1] for f in glob.glob(self.root_dir+path+'*')]
        return ' '.join(files)

    def cat(self, args):
        if len(args) < 1:
            return 'Error: usage: cat <filename>'
        full_path = self.root_dir + args[0]
        if os.path.isdir(full_path):
            return 'Error: Path is a directory'
        try:
            with open(full_path, 'r') as f:
                return f.read()
        except (FileNotFoundError):
            return 'Error: File not found: ' + args[0]

    def write(self, args):
        if len(args) < 2:
            return 'write: usage: write <filename> <content>'
        value = ' '.join(args[1:])
        full_path = self.root_dir + args[0]

        if os.path.exists(full_path):
            return 'Error: Permission Denied'

        if len(value) > current_app.config['max_file_size']:
            return FileTooBig()
        try:

            with open(full_path, 'w') as f:
                f.write(value)
        except PermissionError:
            return f'Permission denied: \'{args[0]}\''

    def mkdir(self, args):
        if len(args) < 1:
            return 'mkdir: usage: mkdir <name>'
        fullpath = self.root_dir + args[0]
        if os.path.exists(fullpath):
            return 'Error: Permission Denied'
        os.mkdir(fullpath)
        return ''

    # Envars operations
    # put the result of code into envar[name]
    def eval_expr(self,args):
        if len(args) < 2:
            return 'eval_expr: usage: eval_expr <varname> <command>'
        out = self.execute_statement(' '.join(args[1:]))
        self.set_envar([args[0], out])
        return out


    def get_envar(self, args):
        if len(args) == 0:
            return self.env_vars
        name = args[0]
        if not name in self.env_vars:
            return EnvarNotFound(f'Cannot find envar {name}')
        
        return self.env_vars[name]

    def set_envar(self, args):
        if len(args) < 2:
            return 'set_envar: usage: set_envar <varname> <value>'
        name = args[0]
        try:
            value = ' '.join(args[1:])
        except:
            value = args[1]

        # Our VM has a limited memory. 
        if len(name) > 30:
            return EnvarNameTooBig()
        if len(str(value)) > 500:
            return EnvarValueTooBig()
        
        if len(self.env_vars) > 50:
            return TooManyEnvars()

        self.env_vars[name] = value 

    def del_envar(self, args):
        name = args[0]
        if not name in self.env_vars:
            return EnvarNotFound(f'Cannot find envar {name}')
        
        del self.env_vars[name]
    
    # Misc 
    def echo(self, args):
        return ' '.join(args)

    def help(self, args):
        help_str = 'Commands available:\n\r' + ' '.join(self.allowlist)
        help_str += '\n\r\n\rExamples:'
        help_str += '\n\recho hello world!'
        help_str += '\n\rset_envar foo bar'
        help_str += '\n\recho {foo}'
        help_str += '\n\rls *'
        return help_str
    
    def base64e(self, args):
        if len(args) < 1:
            return 'base64e: usage: base64e <value>'
        return base64.b64encode(' '.join(args).encode())

    def base64d(self, args):
        if len(args) < 1:
            return 'base64d: usage: base64d <value>'
        return base64.b64decode(args[0]).decode()
    
    def uname(self, args):
        return f'Linux {self.vm_id} 1.0.0-ccOS #1 SMP PREEMPT GNU/Python'

    # WM internals
    def load(self, user_id):
        query = "SELECT * FROM vm WHERE owner = %s"
        vm_id = do_query(query, [user_id])
        if len(vm_id) == 0:
            raise VMNotFound(f'Cannot find VM for user {user_id}')
        
        query = "SELECT * FROM env_var WHERE vm = %s"
        env_vars = do_query(query, [user_id])

        for var in env_vars:
            self.env_vars[var['name']] = var['value']

        query = "SELECT uuid FROM users WHERE username = %s"
        vm_id = do_query(query, [user_id])

        if not os.path.isdir(f'/opt/volumes/volume-{vm_id[0]["uuid"]}'):
            os.mkdir(f'/opt/volumes/volume-{vm_id[0]["uuid"]}')
        return vm_id[0]['uuid']

    def initialize(self, owner):
        query = "INSERT INTO vm(owner) VALUES (%s)"
        do_query(query, [owner], True)
        query = "SELECT uuid FROM users WHERE username = %s"
        vm_id = do_query(query, [owner])
        os.mkdir(f'/opt/volumes/volume-{vm_id[0]["uuid"]}')
        return vm_id[0]['uuid']
       

    def save_vm_status(self):
        query = 'REPLACE INTO env_var(vm,name,value) VALUES(%s,%s,%s)'
        for name, value in self.env_vars.items():
            try:
                do_query(query, [self.owner,name,value], True)
            except Exception:
                print(traceback.print_exc())



    