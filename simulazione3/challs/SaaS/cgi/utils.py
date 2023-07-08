from flask import flash
from functools import wraps
from flask.helpers import url_for

from werkzeug.utils import redirect
from models import Project
from flask import g, abort
import capstone

def flash_form_error(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, category="danger")


# decorator for the autentication
def auth(func):
    @wraps(func)
    def f(*args, **argv):
        if not g.logged:
            return redirect(url_for('interface.register'))
        
        return func(*args, **argv)
    return f

# decorator for login/register
def not_auth(func):
    @wraps(func)
    def f(*args, **argv):
       
        if g.logged:
            return redirect(url_for('interface.index'))

        return func(*args, **argv)
    return f

def project_exists(func):
    @wraps(func)
    def f(*args, **argv):
        pr = Project.query.get(argv['uid'])

        if not pr:
            abort(404)

        g.project = pr
        
        return func(*args, **argv)
    return f



def disasm(code, base_addr=0, arch=capstone.CS_ARCH_X86, mode=capstone.CS_MODE_64):
    insns = []

    md = capstone.Cs(arch, mode)
    off = 0
    while off < len(code):
        for (address, size, mnemonic, op_str) in md.disasm_lite(code[off:], base_addr + off):
            bytes_str = ' '.join(f'{b:02x}' for b in code[off:off+size])
            insns.append(f'{address:04x}\t{bytes_str}\t{mnemonic} {op_str}')
            off += size
        if off < len(code):
            insns.append(f'{base_addr+off:04x}\t{code[off]:02x}\t.byte 0x{code[off]:02x}')
            off += 1

    return '\n'.join(insns)
