import string

def validate_string(inp, lb = 8, ub = 64, charset = string.ascii_letters+string.digits+"="):
    if isinstance(inp, str):
        return all([c in charset for c in inp]) and len(inp) >= lb and len(inp) <= ub
    elif isinstance(inp, bytes):
        return all([bytes([c]) in charset.encode() for c in inp]) and len(inp) >= lb and len(inp) <= ub
    return False
