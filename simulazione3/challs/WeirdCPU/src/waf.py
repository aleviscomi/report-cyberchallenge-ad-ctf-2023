from itertools import zip_longest

# You can modify a program or prevent its execution
# The input is the user program, the output should be the actual program to be sent to the FPGA service
# To prevent the execution of a program just return None


def filter_program(program):

    # Example LOG (print all instructions)
    '''
    print(f'OPCODE\tOP1\tOP2')
    for opcode, op1, op2 in zip_longest(*([iter(program)] * 3)):
      print(f'{opcode:02X}\t{op1:02X}\t{op2:02X}')
    '''

    # Example Modify (add a NOP instruction at the end)
    '''
    program += [0x00, 0x00, 0x00]
    '''

    # Example Prevent Execution
    '''
    return None
    '''

    return program
