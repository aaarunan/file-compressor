import re

window_size = 32 * 1024


def add_to_buffer(search_buffer, byte):
    if len(search_buffer) >= window_size:
        search_buffer.pop()
    search_buffer.append(int.from_bytes(byte, byteorder="big"))


def compress(file_in, file_out) -> None:
    search_buffer = bytearray()
    with open(file_in, "rb") as f_in, open(file_out, "wb") as f_out:
        while byte := f_in.read(1):
            add_to_buffer(search_buffer, byte)
            f_out.write(byte)

            if byte not in search_buffer:
                continue

            start = 0

            temp_array = bytearray(byte)
            matches = 0
            start = 0
            while byte1 := f_in.read(1):
                temp_array.append(int.from_bytes(byte1, byteorder="big"))
                for index, target in enumerate(search_buffer):
                    if target != temp_array[0]:
                        continue
                    temp = find_length(index, temp_array, search_buffer)
                    if temp > matches:
                        matches = temp
                        start = index
            for byte1 in temp_array:
                add_to_buffer(search_buffer, byte1.to_bytes(1, byteorder='big'))

            print(matches)
            if matches != 0:
                f_out.write(start)
                f_out.write(matches)


def find_length(offset, temp_array, search_buffer):
    matches = 0
    for index in range(1, len(temp_array) - 1):
        if index+offset < len(search_buffer) and temp_array[index] == search_buffer[index + offset]:
            matches += 1
    return matches


def main():
    compress("files/empty.txt", "files/lz-output")


if __name__ == "__main__":
    main()
