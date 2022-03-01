import sys
import struct


def main():
    if len(sys.argv) != 2:
        sys.exit("Please provide a file name to run")

    image = None
    filename = sys.argv[1]
    with open(filename, "rb") as inputfile:
        image = inputfile.read()
    print(f"Read {len(image)} bytes from {filename}")

    memory = {}
    for idx in range(0, len(image), 2):
        ww = struct.unpack("<H", image[idx:idx+2])
        memory[idx // 2] = ww[0]
        # print(ww[0], ' ', end='')
    print(f"Memory loaded {len(memory.keys())} words")


if __name__ == '__main__':
    main()