def compress(file_in, file_out) -> None:
    search_buffer = bytearray()
    with open(file_in, "rb") as f_in, open(file_out, "wb") as f_out:
        while byte := f_in.read(1):
            start = search_buffer.find(byte)
            if start == -1:
                search_buffer.append(int.from_bytes(byte, byteorder="big"))
                f_out.write(byte)
                continue

            length = 0

            while byte := f_in.read(1):
                temp = search_buffer.find(start + 1)
                if temp == byte:
                    length += 1
                    return
                search_buffer.append(int.from_bytes(byte, byteorder="big"))
                f_out.write(byte)
                break

            f_out.write(byte)
            f_out.write(start.to_bytes(1, byteorder="big"))
            f_out.write(length.to_bytes(1, byteorder="big"))  # offset
            #Funker ikke bra må reversere search_buffer 
            # så jeg får det siste elemetet jeg la inn
def decompress(file_in, file_out) -> None:
    


def main():
    compress("files/empty.txt", "files/lz-output")


if __name__ == "__main__":
    main()
