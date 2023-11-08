from struct import unpack
from .postings import Posting
from .index import Index
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

            dft = unpack("i", file.read(4))[0]
            docId = 0

            for _ in range(dft):
                docid_gap, tftd = unpack("ii", file.read(8))
                docid_gap += docId
                docId = docid_gap

                positions = []
                position_gap = unpack("i", file.read(4))[0]

                positions.append(position_gap)
                position = positions[0]
                for _ in range(tftd - 1):
                    position_gap = unpack("i", file.read(4))[0]
                    position_gap += position
                    position = position_gap
                    positions.append(position_gap)

                postings.append(Posting(docid_gap, positionList=positions))

        return postings
