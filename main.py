from collections import deque
import struct
import sys
import opcode


def main():
    if len(sys.argv) != 2:
        sys.exit("Please provide a file name to run")

    filename = sys.argv[1]
    with open(filename, "rb") as image_file:
        image = image_file.read()
    print(f"Read {len(image)} bytes from {filename}")

    memory = {}
    for idx in range(0, len(image), 2):
        ww = struct.unpack("<H", image[idx:idx+2])
        memory[idx // 2] = ww[0]
        # print(ww[0], ' ', end='')
    print(f"Memory loaded {len(memory.keys())} words")

    registers = [0, 0, 0, 0, 0, 0, 0, 0]
    stack = deque()
    # pc, list_end = 800, 900
    pc = 0

    while True:
        opc = opcode.dispatch(pc, memory)
        npc, registers, stack, memory, continue_flag = opc.execute(pc, registers, stack, memory)
        # if not continue_flag:
        #     print(f"Program halted at PC = {pc}")
        #     break
        if memory[pc] == 20:
            print(f"Found IN - program halted at PC = {pc}")
            break
        if npc == 1239:
            print(f"Jumping to 1239 from PC = {pc}")
            break
        pc = npc

        # opc = opcode.dispatch(pc, memory)
        # npc, str1, str2 = opc.list(pc, memory)
        # print(f"{pc:5}: {str1}  ; {str2}")
        #
        # pc = npc
        # if pc > list_end:
        #     break


        #
        # opcode, pc = memory[pc], pc + 1
        # if opcode == 0:
        #     # halt: 0
        #     #   stop execution and terminate the program
        #     break
        # elif opcode == 1:
        #     # set: 1 a b
        #     #   set register <a> to the value of <b>
        #     a, pc = interpret(memory[pc], registers), pc + 1
        #     b, pc = interpret(memory[pc], registers), pc + 1
        #     registers[a] = b
        # elif opcode == 6:
        #     # jmp: 6 a
        #     #   jump to <a>
        #     a, pc = interpret(memory[pc], registers), pc + 1
        #     pc = a
        # elif opcode == 7:
        #     # jt: 7 a b
        #     #   if <a> is nonzero, jump to <b>
        #     a, pc = interpret(memory[pc], registers), pc + 1
        #     b, pc = interpret(memory[pc], registers), pc + 1
        #     pc = b if a != 0 else pc
        # elif opcode == 8:
        #     # jf: 8 a b
        #     #   if <a> is zero, jump to <b>
        #     a, pc = interpret(memory[pc], registers), pc + 1
        #     b, pc = interpret(memory[pc], registers), pc + 1
        #     pc = b if a == 0 else pc
        # elif opcode == 19:
        #     # out: 19 a
        #     #   write the character represented by ascii code <a> to the terminal
        #     a, pc = interpret(memory[pc], registers), pc + 1
        #     print(chr(a), end='')
        # elif opcode == 21:
        #     # noop: 21
        #     #   no operation
        #     pass
        # else:
        #     print(f"Unhandled opcode {opcode}")


if __name__ == '__main__':
    main()
