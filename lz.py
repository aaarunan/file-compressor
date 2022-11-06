import tqdm
from collections import deque

MAX_SEARCH_LENGTH = 127
MIN_COMMON_SUBSTRING_LENGTH = 5


class SearchBuffer:
    WINDOW_SIZE = 64 * 1024

    def __init__(self) -> None:
        self.search_buffer = deque(bytearray())
        self.index = 0

    def write(self, byte: bytes) -> None:
        if self.index >= self.WINDOW_SIZE:
            self.search_buffer.popleft()
        else:
            self.index += 1
        self.search_buffer.append(byte)


def signed_int_to_byte(num: int) -> bytes:
    return num.to_bytes(1, byteorder="big", signed=True)


def byte_to_signed_int(byte: int) -> int:
    return int.from_bytes(byte, byteorder="big", signed=True)


def byte_to_int(byte: bytes) -> int:
    return int.from_bytes(byte, byteorder="big")


def int_to_byte(num: int) -> bytes:
    return num.to_bytes(1, byteorder="big")


def longest_common_substring(
    buffer: bytearray, search_buffer: SearchBuffer, target: bytes, current_position: int
) -> tuple[int, int]:
    length = 0
    offset = 0

    for index, byte in enumerate(search_buffer.search_buffer):
        if byte != target:
            continue

        i = 1
        temp_length = 1

        while True:
            if (
                (current_position + i) < len(buffer)
                and (index + i) < search_buffer.index
                and buffer[current_position + i]
                == search_buffer.search_buffer[index + i]
                and temp_length < MAX_SEARCH_LENGTH
            ):
                temp_length += 1

            else:
                if temp_length > length:
                    length = temp_length
                    offset = index
                break

            i += 1

    return search_buffer.index - offset, length


def compress(file_path_in: str, file_path_out: str) -> None:

    i = 0
    last = 0
    search_buffer = SearchBuffer()
    buffer = open(file_path_in, "rb").read()
    pbar = tqdm.tqdm(total=len(buffer))

    with open(file_path_out, "wb") as f_out:
        while i < len(buffer):
            current_byte = buffer[i]

            if (i - last) >= MAX_SEARCH_LENGTH - 10:
                f_out.write(signed_int_to_byte(-(i - last)))
                while last < i:
                    f_out.write(int_to_byte(buffer[last]))
                    last += 1

            if current_byte not in search_buffer.search_buffer:
                search_buffer.write(current_byte)
                i += 1
                pbar.update(1)
                continue

            offset, length = longest_common_substring(
                buffer, search_buffer, current_byte, i
            )

            if length > 5:
                f_out.write(signed_int_to_byte(-(i - last)))
                while last < i:
                    f_out.write(int_to_byte(buffer[last]))
                    last += 1

                for _ in range(length):
                    search_buffer.write(buffer[i])
                    i += 1

                last = i

                f_out.writelines(
                    [signed_int_to_byte(length), offset.to_bytes(2, byteorder="big")]
                )
            else:
                for _ in range(length):
                    search_buffer.write(buffer[i])
                    i += 1

            pbar.update(length)

        f_out.write(signed_int_to_byte(-(i - last)))
        while last < i:
            f_out.write(int_to_byte(buffer[last]))
            last += 1


def decompress(file_path_in, file_path_out):
    buffer = bytearray()
    search_buffer = SearchBuffer()
    buffer = open(file_path_in, "rb").read()
    i = 0
    pbar = tqdm.tqdm(total=len(buffer))

    with open(file_path_out, "wb") as f_out:
        while i < len(buffer):
            repetitions = byte_to_signed_int(int_to_byte(buffer[i]))
            i += 1
            pbar.update(1)
            if repetitions <= 0:
                for _ in range(-repetitions):
                    f_out.write(int_to_byte(buffer[i]))
                    search_buffer.write(buffer[i])
                    i += 1
                    pbar.update(1)
            else:
                offset = buffer[i] << 8 | buffer[i + 1]
                for _ in range(repetitions):
                    f_out.write(
                        int_to_byte(
                            search_buffer.search_buffer[search_buffer.index - offset]
                        )
                    )
                    search_buffer.write(
                        search_buffer.search_buffer[search_buffer.index - offset]
                    )
                i += 2
                pbar.update(2)
