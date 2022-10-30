import re
from sys import byteorder
import tqdm

window_size = 32 * 1024 

window = bytearray()
buffer = bytearray()


def add_to_window(byte):
    if len(window) >= window_size:
        window.pop()
    window.append(byte)
    #window.append(int.from_bytes(byte, byteorder="big"))


def compress(file_in, file_out) -> None:
    with open(file_in, "rb") as f_in:
        while byte := f_in.read(1):
            buffer.append(int.from_bytes(byte, byteorder='big'))


    with open(file_out, "wb") as f_out:
        iterator =  enumerate(tqdm.tqdm(buffer))
        for index, byte in iterator:
            add_to_window(byte)
            f_out.write(byte.to_bytes(1, byteorder='big'))

            if byte not in window:
                continue
            (start, matches) = findLongestMatch(index)

            if matches is not None:
                f_out.write(start.to_bytes(1, byteorder='big'))
                f_out.write(matches.to_bytes(1, byteorder='big'))
                for _ in range(matches):
                    next(iterator)


def findLongestMatch(current_position):
    end_of_buffer = min(current_position + window_size, len(buffer) + 1)

    best_match_distance = -1
    best_match_length = -1

    for j in range(current_position + 2, end_of_buffer):

        start_index = max(0, current_position - window_size)
        substring = buffer[current_position:j]

        for i in range(start_index, current_position):

            repetitions = len(substring) // (current_position - i)

            last = len(substring) % (current_position - i)

            matched_string = buffer[i:current_position] * repetitions + buffer[i:i+last]

            if matched_string == substring and len(substring) > best_match_length:
                best_match_distance = current_position - i 
                best_match_length = len(substring)

    if best_match_distance > 0 and best_match_length > 0:
        return (best_match_distance, best_match_length)
    return (None, None)


def main():
    compress("files/diverse.txt", "files/lz-output")


if __name__ == "__main__":
    main()
