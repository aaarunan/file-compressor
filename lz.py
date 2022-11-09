import tqdm
from collections import deque

MAX_SEARCH_LENGTH = 127
MIN_COMMON_SUBSTRING_LENGTH = 6


class SearchBuffer(deque):
    WINDOW_SIZE = 32 * 1024

    def append(self, x: bytes) -> None:
        if len(self) > self.WINDOW_SIZE:
            self.popleft()
        super().append(x)


def _signed_int_to_byte(num: int) -> bytes:
    return num.to_bytes(1, byteorder="big", signed=True)


def _byte_to_signed_int(byte: int) -> int:
    return int.from_bytes(byte, byteorder="big", signed=True)

def _int_to_byte(num: int) -> bytes:
    return num.to_bytes(1, byteorder="big")


def _longest_common_substring(
    data: bytearray, buffer: SearchBuffer, target: bytes, position: int
) -> tuple[int, int]:
    length = 0
    offset = 0

    for index, byte in enumerate(buffer):
        if byte != target:
            continue

        i = 1
        temp_length = 1

        while True:
            if (
                (position + i) < len(data)
                and (index + i) < len(buffer)
                and data[position + i] == buffer[index + i]
                and temp_length < MAX_SEARCH_LENGTH
            ):
                temp_length += 1

            else:
                if temp_length > length:
                    length = temp_length
                    offset = index
                break

            i += 1

    return len(buffer) - offset, length


def compress(file_path_in: str, file_path_out: str) -> None:

    i = 0
    last = 0
    data = open(file_path_in, "rb").read()
    buffer = SearchBuffer()
    pbar = tqdm.tqdm(total=len(data))

    with open(file_path_out, "wb") as f_out:
        while i < len(data):
            current_byte = data[i]

            if (i - last) >= MAX_SEARCH_LENGTH - 10:
                f_out.write(_signed_int_to_byte(-(i - last)))
                while last < i:
                    f_out.write(_int_to_byte(data[last]))
                    last += 1

            if current_byte not in buffer:
                buffer.append(current_byte)
                i += 1
                pbar.update(1)
                continue

            offset, length = _longest_common_substring(
                data, buffer, current_byte, i
            )

            if length > MIN_COMMON_SUBSTRING_LENGTH:
                f_out.write(_signed_int_to_byte(-(i - last)))
                while last < i:
                    f_out.write(_int_to_byte(data[last]))
                    last += 1

                for _ in range(length):
                    buffer.append(data[i])
                    i += 1

                last = i

                f_out.writelines(
                    [_signed_int_to_byte(length), offset.to_bytes(2, byteorder="big")]
                )
            else:
                for _ in range(length):
                    buffer.append(data[i])
                    i += 1

            pbar.update(length)

        f_out.write(_signed_int_to_byte(-(i - last)))
        while last < i:
            f_out.write(_int_to_byte(data[last]))
            last += 1


def decompress(file_path_in, file_path_out):
    data = bytearray()
    buffer = SearchBuffer()
    data = open(file_path_in, "rb").read()
    i = 0
    pbar = tqdm.tqdm(total=len(data))

    with open(file_path_out, "wb") as f_out:
        while i < len(data):
            repetitions = _byte_to_signed_int(_int_to_byte(data[i]))
            i += 1
            pbar.update(1)
            if repetitions <= 0:
                for _ in range(-repetitions):
                    f_out.write(_int_to_byte(data[i]))
                    buffer.append(data[i])
                    i += 1
                    pbar.update(1)
            else:
                offset = data[i] << 8 | data[i + 1]
                for _ in range(repetitions):
                    f_out.write(_int_to_byte(buffer[len(buffer) - offset]))
                    buffer.append(buffer[len(buffer) - offset])
                i += 2
                pbar.update(2)
