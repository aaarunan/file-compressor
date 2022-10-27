from dataclasses import dataclass
import heapq

import sys
sys.getdefaultencoding()

@dataclass
class TreeNode:
    count: int = None
    letter: str = None
    left: any = None
    right: any = None

    def __lt__(self, other):
        return self.count < other.count


def parse_file(file: str) -> list[int]:
    nums = [0] * 256
    file_as_byte = []
    with open(file, "rb") as f:
        while byte := f.read(1):
            position = int.from_bytes(byte, byteorder="big")
            file_as_byte.append(position)
            nums[position] = nums[position] + 1
    return [nums, file_as_byte]


def write_to_file(
    file: str, frequencies: list[int], codes: list[int], file_as_bytes: list[int]
) -> None:
    string = ""
    for byte in file_as_bytes:
        string += str((codes[byte]))

    buffer = []
    for i in range(0, len(string), 8):
        buffer.append(int(string[i : i + 8], 2))

    with open(file, "wb") as f:
        # Write frequency table
        for num in frequencies:
            byte = num.to_bytes(2, byteorder="big")
            f.write(byte)
        # write codes
        for integer in buffer:
            f.write(integer.to_bytes(1, byteorder="big"))
        print()


def make_nodes(nums: list[int]) -> list[TreeNode]:
    nodes = []
    for index, num in enumerate(nums):
        nodes.append(TreeNode(num, index, None, None))
    return nodes


def make_codes(root: TreeNode, code: str, bitstrings: list[list[int]]):
    if root.left is None and root.right is None:
        bitstrings[root.letter] = code
        return
    make_codes(root.left, code + "0", bitstrings)
    make_codes(root.right, code + "1", bitstrings)


def make_tree(priorities: list[TreeNode]) -> TreeNode:
    while len(priorities) > 1:
        left = heapq.heappop(priorities)
        right = heapq.heappop(priorities)
        total_count = left.count + right.count
        node = TreeNode(total_count, None, left, right)
        heapq.heappush(priorities, node)
    return priorities[0]


def compress(file_in, file_out):
    frequencies, file_as_bytes = parse_file(file_in)
    nodes = make_nodes(frequencies)
    tree = make_tree(nodes)
    codes = [None] * 256
    make_codes(tree, "", codes)
    write_to_file(file_out, frequencies, codes, file_as_bytes)


def decompress(file_in, file_out):
    frequencies = [0] * 256
    with open(file_in, "rb") as f_in, open(file_out, "wb") as f_out:
        for index in range(256):
            byte = f_in.read(2)
            num = int.from_bytes(byte, byteorder="big")
            frequencies[index] = num

        tree = make_tree(make_nodes(frequencies))
        temp_tree = tree

        while byte := f_in.read(1):
            num = int.from_bytes(byte, byteorder="big")
            byte_string = ("{:0%db}" % 8).format(num)

            for bit in byte_string:
                bit = int(bit)
                if temp_tree.left is None and temp_tree.right is None:
                    f_out.write(temp_tree.letter.to_bytes(1, byteorder="big"))
                    temp_tree = tree
                if bit == 1:
                    temp_tree = temp_tree.right
                if bit == 0:
                    temp_tree = temp_tree.left


def main():
    working_dir = "files/"
    output = working_dir + "compressed"

    if len(sys.argv) == 1:
        print("<compress/decompress> <filepath>")
    if sys.argv[1] == "compress":
        if sys.argv[1] == "":
            print("choose a file")
            sys.exit()
        compress(working_dir + sys.argv[2], output)
        return
    if sys.argv[1] == "decompress":
        decompress(output, working_dir + "uncompressed.txt")
        return
    print("compress or decompress?")


if __name__ == "__main__":
    main()
    # test_make_tree()
