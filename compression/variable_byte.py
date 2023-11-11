def vb_encode(num: int):
    bytes_list = bytearray()
    if num == 0:
        bytes_list.append(num & 127)
    while num != 0:
        if len(bytes_list) == 0:
            bytes_list.append(num & 127)
        else:
            bytes_list.insert(0, num & 127)
        num = num >> 7
    bytes_list[-1] = bytes_list[-1] | 128

    return bytes_list


def vb_decode(encoded_bytes):
    decoded_value = 0

    for i in range(len(encoded_bytes)):
        temp = encoded_bytes[i] & 127
        decoded_value = decoded_value | temp
        if i != len(encoded_bytes) - 1:
            decoded_value = decoded_value << 7

    return decoded_value
