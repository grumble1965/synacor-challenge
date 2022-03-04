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

    # dump_program(memory, 320)
    run_machine(memory, pc, registers, stack)


def run_machine(memory, pc, registers, stack):
    while True:
        opc = opcode.dispatch(pc, memory)
        npc, registers, stack, memory, continue_flag = opc.execute(pc, registers, stack, memory)
        # if not continue_flag:
        #     print(f"Program halted at PC = {pc}")
        #     break
        # if memory[pc] == 20:
        #     print(f"Found IN - program halted at PC = {pc}")
        #     break
        if npc == 1239:
            print(f"Jumping to 1239 from PC = {pc}")
            break
        pc = npc


def dump_program(memory, start, length=100):
    pc = start
    while pc < start+length:
        opc = opcode.dispatch(pc, memory)
        npc, str1, str2 = opc.list(pc, memory)
        print(f"{pc:5}: {str1}  ; {str2}")
        pc = npc


if __name__ == '__main__':
    main()
