from abc import ABC, abstractmethod
from collections import deque

RegType = list[int]
MemType = dict[int, int]
StackType = deque


class Opcode(ABC):
    _list_field_1_width = 20
    _list_field_2_width = 20

    @abstractmethod
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        pass

    @abstractmethod
    def list(self, pc, memory: MemType) -> (int, str, str):
        pass


class HaltOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        return pc + 1, registers, stack, memory, False

    def list(self, pc, memory: MemType) -> (int, str, str):
        return pc + 1, "0".ljust(Opcode._list_field_1_width), "halt".ljust(Opcode._list_field_2_width)


class SetOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        dest = imm_interpret(memory[pc + 1]) - 32768
        val = read_interpret(memory[pc + 2], registers)
        # print(f"Set: dest {memory[pc+1]}(raw) {dest}(imm) = {val}")
        registers[dest] = val
        return pc + 3, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b = memory[pc + 1], memory[pc + 2]
        al, bl = list_interpret(a), list_interpret(b)
        return pc + 3, f"1 {a} {b}".ljust(Opcode._list_field_1_width), f"set {al} {bl}".ljust(
            Opcode._list_field_2_width)


class PushOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = read_interpret(memory[pc + 1], registers)
        stack.append(a)
        # print(f"PUSH {a} onto {stack}")
        return pc + 2, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a = memory[pc + 1]
        al = list_interpret(a)
        return pc + 2, f"2 {a}".ljust(Opcode._list_field_1_width), f"push {al}".ljust(Opcode._list_field_2_width)


class PopOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = imm_interpret(memory[pc + 1])
        if len(stack) == 0:
            print(f"Error: Popping from empty stack at pc = {pc}, {stack}")
            val, halt = 0, False
        else:
            val, halt = stack.pop(), True
        if 32768 <= a <= 32775:
            registers[a - 32768] = val
        else:
            memory[a] = val
        return pc + 2, registers, stack, memory, halt

    def list(self, pc, memory: MemType) -> (int, str, str):
        a = memory[pc + 1]
        al = list_interpret(a)
        return pc + 2, f"3 {a}".ljust(Opcode._list_field_1_width), f"pop {al}".ljust(Opcode._list_field_2_width)


class EqOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = imm_interpret(memory[pc + 1])
        b = read_interpret(memory[pc + 2], registers)
        c = read_interpret(memory[pc + 3], registers)
        res = 1 if b == c else 0
        if 32768 <= a <= 32775:
            registers[a - 32768] = res
        else:
            memory[a] = res
        return pc + 4, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b, c = memory[pc + 1], memory[pc + 2], memory[pc + 3]
        al, bl, cl = list_interpret(a), list_interpret(b), list_interpret(c)
        return pc + 4, f"4 {a} {b} {c}".ljust(Opcode._list_field_1_width), f"eq {al} {bl} {cl}".ljust(
            Opcode._list_field_2_width)


class GtOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = imm_interpret(memory[pc + 1])
        b = read_interpret(memory[pc + 2], registers)
        c = read_interpret(memory[pc + 3], registers)
        res = 1 if b > c else 0
        if 32768 <= a <= 32775:
            registers[a - 32768] = res
        else:
            memory[a] = res
        return pc + 4, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b, c = memory[pc + 1], memory[pc + 2], memory[pc + 3]
        al, bl, cl = list_interpret(a), list_interpret(b), list_interpret(c)
        return pc + 4, f"5 {a} {b} {c}".ljust(Opcode._list_field_1_width), f"gt {al} {bl} {cl}".ljust(
            Opcode._list_field_2_width)


class JumpOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = read_interpret(memory[pc + 1], registers)
        return a, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a = memory[pc + 1]
        al = list_interpret(a)
        return pc + 2, f"6 {a}".ljust(Opcode._list_field_1_width), f"jmp {al}".ljust(Opcode._list_field_2_width)


class JumpTrueOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = read_interpret(memory[pc + 1], registers)
        b = read_interpret(memory[pc + 2], registers)
        return b if a != 0 else pc + 3, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b = memory[pc + 1], memory[pc + 2]
        al, bl = list_interpret(a), list_interpret(b)
        return pc + 3, f"7 {a} {b}".ljust(Opcode._list_field_1_width), f"jt {al} {bl}".ljust(Opcode._list_field_2_width)


class JumpFalseOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = read_interpret(memory[pc + 1], registers)
        b = read_interpret(memory[pc + 2], registers)
        return b if a == 0 else pc + 3, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b = memory[pc + 1], memory[pc + 2]
        al, bl = list_interpret(a), list_interpret(b)
        return pc + 3, f"8 {a} {b}".ljust(Opcode._list_field_1_width), f"jf {al} {bl}".ljust(Opcode._list_field_2_width)


class AddOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = imm_interpret(memory[pc + 1])
        b = read_interpret(memory[pc + 2], registers)
        c = read_interpret(memory[pc + 3], registers)
        res = (b + c) % 32768
        if 32768 <= a <= 32775:
            registers[a - 32768] = res
        else:
            memory[a] = res
        return pc + 4, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b, c = memory[pc + 1], memory[pc + 2], memory[pc + 3]
        al, bl, cl = list_interpret(a), list_interpret(b), list_interpret(c)
        return pc + 4, f"9 {a} {b} {c}".ljust(Opcode._list_field_1_width), f"add {al} {bl} {cl}".ljust(
            Opcode._list_field_2_width)


class MultOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = imm_interpret(memory[pc + 1])
        b = read_interpret(memory[pc + 2], registers)
        c = read_interpret(memory[pc + 3], registers)
        res = (b * c) % 32768
        if 32768 <= a <= 32775:
            registers[a - 32768] = res
        else:
            memory[a] = res
        return pc + 4, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b, c = memory[pc + 1], memory[pc + 2], memory[pc + 3]
        al, bl, cl = list_interpret(a), list_interpret(b), list_interpret(c)
        return pc + 4, f"10 {a} {b} {c}".ljust(Opcode._list_field_1_width), f"mult {al} {bl} {cl}".ljust(
            Opcode._list_field_2_width)


class ModOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = imm_interpret(memory[pc + 1])
        b = read_interpret(memory[pc + 2], registers)
        c = read_interpret(memory[pc + 3], registers)
        res = (b % c) % 32768
        if 32768 <= a <= 32775:
            registers[a - 32768] = res
        else:
            memory[a] = res
        return pc + 4, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b, c = memory[pc + 1], memory[pc + 2], memory[pc + 3]
        al, bl, cl = list_interpret(a), list_interpret(b), list_interpret(c)
        return pc + 4, f"11 {a} {b} {c}".ljust(Opcode._list_field_1_width), f"mod {al} {bl} {cl}".ljust(
            Opcode._list_field_2_width)


class AndOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = imm_interpret(memory[pc + 1])
        b = read_interpret(memory[pc + 2], registers)
        c = read_interpret(memory[pc + 3], registers)
        res = (b & c) % 32768
        if 32768 <= a <= 32775:
            registers[a - 32768] = res
        else:
            memory[a] = res
        return pc + 4, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b, c = memory[pc + 1], memory[pc + 2], memory[pc + 3]
        al, bl, cl = list_interpret(a), list_interpret(b), list_interpret(c)
        return pc + 4, f"12 {a} {b} {c}".ljust(Opcode._list_field_1_width), f"and {al} {bl} {cl}".ljust(
            Opcode._list_field_2_width)


class OrOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = imm_interpret(memory[pc + 1])
        b = read_interpret(memory[pc + 2], registers)
        c = read_interpret(memory[pc + 3], registers)
        res = (b | c) % 32768
        if 32768 <= a <= 32775:
            registers[a - 32768] = res
        else:
            memory[a] = res
        return pc + 4, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b, c = memory[pc + 1], memory[pc + 2], memory[pc + 3]
        al, bl, cl = list_interpret(a), list_interpret(b), list_interpret(c)
        return pc + 4, f"13 {a} {b} {c}".ljust(Opcode._list_field_1_width), f"or {al} {bl} {cl}".ljust(Opcode._list_field_2_width)


class NotOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = imm_interpret(memory[pc + 1])
        b = read_interpret(memory[pc + 2], registers)
        res = (~b) % 32768
        if 32768 <= a <= 32775:
            registers[a - 32768] = res
        else:
            memory[a] = res
        return pc + 3, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b = memory[pc + 1], memory[pc + 2]
        al, bl = list_interpret(a), list_interpret(b)
        return pc + 4, f"14 {a} {b}".ljust(Opcode._list_field_1_width), f"not {al} {bl}".ljust(
            Opcode._list_field_2_width)


class ReadMemOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = imm_interpret(memory[pc + 1])
        b = read_interpret(memory[pc + 2], registers)
        res = memory[b] % 32768
        if 32768 <= a <= 32775:
            registers[a - 32768] = res
        else:
            memory[a] = res
        # print(f"RMEM {a} {b} gives {res} at pc = {pc}")
        return pc + 3, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b = memory[pc + 1], memory[pc + 2]
        al, bl = list_interpret(a), list_interpret(b)
        return pc + 3, f"15 {a} {b}".ljust(Opcode._list_field_1_width), f"rmem {al} {bl}".ljust(
            Opcode._list_field_2_width)


class WriteMemOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = read_interpret(memory[pc + 1], registers)
        b = read_interpret(memory[pc + 2], registers)
        res = b % 32768
        #print(f"WMEM at pc = {pc}")
        if 32768 <= a <= 32775:
            registers[a - 32768] = res
        else:
            memory[a] = res
        return pc + 3, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a, b = memory[pc + 1], memory[pc + 2]
        al, bl = list_interpret(a), list_interpret(b)
        return pc + 3, f"16 {a} {b}".ljust(Opcode._list_field_1_width), f"wmem {al} {bl}".ljust(
            Opcode._list_field_2_width)


class CallOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = read_interpret(memory[pc + 1], registers)
        stack.append(pc + 2)
        return a, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a = memory[pc + 1]
        al = list_interpret(a)
        return pc + 2, f"17 {a}".ljust(Opcode._list_field_1_width), f"call {al}".ljust(Opcode._list_field_2_width)


class ReturnOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        if not stack:
            print(f"Error: Returning from empty stack at pc = {pc}")
            val = pc + 1
        else:
            val = stack.pop()
        return val, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        return pc + 1, f"18".ljust(Opcode._list_field_1_width), f"ret".ljust(Opcode._list_field_2_width)


class OutOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = imm_interpret(memory[pc + 1])
        print(chr(a), end='')
        return pc + 2, registers, stack, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        a = list_interpret(memory[pc + 1])
        ch = ascii(chr(int(a)))
        return pc + 2, f"19 {a}".ljust(Opcode._list_field_1_width), f"out {ch}".ljust(Opcode._list_field_2_width)


class InOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        a = memory[pc + 1]
        print(f"IN doesn't work at pc {pc}")
        return pc + 2, registers, stack, memory, False

    def list(self, pc, memory: MemType) -> (int, str, str):
        a = memory[pc + 1]
        al = list_interpret(a)
        return pc + 2, f"20 {a}".ljust(Opcode._list_field_1_width), f"in {al}".ljust(Opcode._list_field_2_width)


class NoopOpcode(Opcode):
    def execute(self, pc: int, registers: RegType, stack: StackType, memory: MemType) \
            -> (int, RegType, StackType, MemType, bool):
        return pc + 1, registers, memory, True

    def list(self, pc, memory: MemType) -> (int, str, str):
        return pc + 1, "21".ljust(Opcode._list_field_1_width), "noop".ljust(Opcode._list_field_2_width)


class UndefinedOpcode(Opcode):
    def execute(self, pc: int, reg: RegType, stack: StackType, mem: MemType) \
            -> (int, RegType, MemType, bool):
        raise Exception(f"Can't execute undefined Opcode {mem[pc]}")

    def list(self, pc: int, mem: MemType) -> (int, str, str):
        op = mem[pc]
        return pc + 1, f"{op}".ljust(Opcode._list_field_1_width), "???".ljust(Opcode._list_field_2_width)


_table = {
    0: HaltOpcode(),
    1: SetOpcode(),
    2: PushOpcode(),
    3: PopOpcode(),
    4: EqOpcode(),
    5: GtOpcode(),
    6: JumpOpcode(),
    7: JumpTrueOpcode(),
    8: JumpFalseOpcode(),
    9: AddOpcode(),
    10: MultOpcode(),
    11: ModOpcode(),
    12: AndOpcode(),
    13: OrOpcode(),
    14: NotOpcode(),
    15: ReadMemOpcode(),
    16: WriteMemOpcode(),
    17: CallOpcode(),
    18: ReturnOpcode(),
    19: OutOpcode(),
    20: InOpcode(),
    21: HaltOpcode()
}
_undefined_opcode = UndefinedOpcode()


def dispatch(pc, memory) -> Opcode:
    if pc not in memory:
        raise Exception(f"Undefined address {pc}")
    inst = memory[pc]
    if inst in _table:
        return _table[inst]
    else:
        return _undefined_opcode


def read_interpret(num, registers):
    # - numbers 0..32767 mean a literal value
    # - numbers 32768..32775 instead mean registers 0..7
    # - numbers 32776..65535 are invalid
    if 0 <= num <= 32767:
        return num
    elif 32768 <= num <= 32775:
        return registers[num - 32768]
    else:
        print(f"interpret: unhandled number {num}")


def imm_interpret(num):
    # - numbers 0..32767 mean a literal value
    # - numbers 32768..32775 instead mean registers 0..7
    # - numbers 32776..65535 are invalid
    if 0 <= num <= 32767:
        return num
    elif 32768 <= num <= 32775:
        return num
    else:
        print(f"interpret: unhandled number {num}")


def list_interpret(num):
    # - numbers 0..32767 mean a literal value
    # - numbers 32768..32775 instead mean registers 0..7
    # - numbers 32776..65535 are invalid
    if 0 <= num <= 32767:
        return f"{num}"
    elif 32768 <= num <= 32775:
        return f"R{num - 32768}"
    else:
        print(f"list_interpret: unhandled number {num}")


def main():
    pass


if __name__ == '__main__':
    main()
