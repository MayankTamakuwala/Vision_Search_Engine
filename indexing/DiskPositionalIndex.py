import struct
from .postings import Posting
from .index import Index
from pymongo import MongoClient
from indexing import get_client


class DiskPositionalIndex(Index):
    def __init__(self, path):
        self.path = path
        self.__client = get_client()
        self.__collection = self.__client["Vocabularies"]["TermTrack"]

    def get_postings(self, term):

        byte_position_object = self.__collection.find_one({"term": term})

        if byte_position_object is None:
            return None
        else:
            byte_position = byte_position_object["byte_position"]

        with open(self.path, "rb") as file:
            file.seek(byte_position)

            postings = []

            dft = struct.unpack("i", file.read(4))[0]  # Read document frequency (dft)

            for _ in range(dft):
                docid_gap, tftd = struct.unpack("ii", file.read(8))  # Read docid gap and term frequency (tftd)

                positions = []
                position_gap = struct.unpack("i", file.read(4))[0]  # Read position gap

                positions.append(position_gap)

                for _ in range(tftd - 1):
                    position_gap = struct.unpack("i", file.read(4))[0]  # Read position gap
                    positions.append(positions[-1] + position_gap)

                postings.append(Posting(docid_gap, tftd, positions))

        return postings
