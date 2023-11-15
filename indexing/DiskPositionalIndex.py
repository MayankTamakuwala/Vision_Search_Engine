from .postings import Posting
from .index import Index
from indexing import get_client
from compression.variable_byte import vb_decode
from pathlib import Path


def file_content_decoder(f):
    temp = bytearray()
    x = f.read(1)
    y = int.from_bytes(x, "big")
    while y & 128 != 128:
        temp.append(y)
        x = f.read(1)
        y = int.from_bytes(x, "big")
    temp.append(y)
    return vb_decode(temp)


class DiskPositionalIndex(Index):
    def __init__(self, path):
        self.path = path
        self.__client = get_client()
        self.__collection = self.__client["Vocabularies"]["1" + path[1:] if path[0] == "." else path]

    def get_postings(self, term):

        byte_position_object = self.__collection.find_one({"term": term})

        if byte_position_object is None:
            return None
        else:
            byte_position = byte_position_object["byte_position"]

        with open(Path(self.path), "rb") as file:
            file.seek(byte_position)

            postings = []

            dft = file_content_decoder(file)
            docId = 0

            for _ in range(dft):
                docid_gap = file_content_decoder(file)

                tftd = file_content_decoder(file)
                docid_gap += docId
                docId = docid_gap

                positions = []
                position_gap = file_content_decoder(file)

                positions.append(position_gap)
                position = positions[0]
                for _ in range(tftd - 1):
                    position_gap = file_content_decoder(file)
                    position_gap += position
                    position = position_gap
                    positions.append(position_gap)

                postings.append(Posting(docid_gap, positionList=positions))

        return postings
