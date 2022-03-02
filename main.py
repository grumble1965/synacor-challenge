# from collections import deque
import struct
import sys


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
    # stack = deque()
    pc = 0

    while True:
        opcode, pc = memory[pc], pc + 1
        if opcode == 0:
            # halt: 0
            #   stop execution and terminate the program
            break
        elif opcode == 1:
            # set: 1 a b
            #   set register <a> to the value of <b>
            a, pc = interpret(memory[pc], registers), pc + 1
            b, pc = interpret(memory[pc], registers), pc + 1
            registers[a] = b
        elif opcode == 6:
            # jmp: 6 a
            #   jump to <a>
            a, pc = interpret(memory[pc], registers), pc + 1
            pc = a
        elif opcode == 7:
            # jt: 7 a b
            #   if <a> is nonzero, jump to <b>
            a, pc = interpret(memory[pc], registers), pc + 1
            b, pc = interpret(memory[pc], registers), pc + 1
            pc = b if a != 0 else pc
        elif opcode == 8:
            # jf: 8 a b
            #   if <a> is zero, jump to <b>
            a, pc = interpret(memory[pc], registers), pc + 1
            b, pc = interpret(memory[pc], registers), pc + 1
            pc = b if a == 0 else pc
        elif opcode == 19:
            # out: 19 a
            #   write the character represented by ascii code <a> to the terminal
            a, pc = interpret(memory[pc], registers), pc + 1
            print(chr(a), end='')
        elif opcode == 21:
            # noop: 21
            #   no operation
            pass
        else:
            print(f"Unhandled opcode {opcode}")


def interpret(num, registers):
    # - numbers 0..32767 mean a literal value
    # - numbers 32768..32775 instead mean registers 0..7
    # - numbers 32776..65535 are invalid
    if 0 <= num <= 32767:
        return num
    elif 32768 <= num <= 32775:
        return registers[num - 32768]
    else:
        print(f"interpret: unhandled number {num}")


if __name__ == '__main__':
    main()
