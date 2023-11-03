from struct import pack
from pymongo import MongoClient


def get_client():
    CONNECTION_STRING = ("mongodb+srv://mayank:12345@searchenginevocab.hfbqnqe.mongodb.net/?retryWrites=true&w"
                         "=majority")

    return MongoClient(CONNECTION_STRING)


class DiskIndexWriter:

    def __init__(self, postings_path):
        self.__client = get_client()
        self.__collection = self.__client["Vocabularies"]["TermTrack"]
        self.postings_file = open(postings_path, "wb")

    def __del__(self):
        self.__client.close()
        self.postings_file.close()

    def add_position(self, term, byte_position):
        self.__collection.insert_one({
            "term": term,
            "byte_position": byte_position
        })

    def write_index(self, index):

        print("\nCreating file on disk...\n")

        for term in index:

            byte_position = self.postings_file.tell()

            self.add_position(term, byte_position)

            postings_list = index.get_postings(term)

            dft = len(postings_list)

            self.postings_file.write(pack("i", dft))

            docId_gap = 0

            for posting in postings_list:
                doc_id = posting.get_doc_id() - docId_gap
                docId_gap = posting.get_doc_id()

                self.postings_file.write(pack("i", doc_id))

                tftd = len(posting.get_positions())

                self.postings_file.write(pack("i", tftd))

                position_gap = 0
                for p in posting.positions:
                    position = p - position_gap
                    position_gap = p
                    self.postings_file.write(pack("i", position))

        print("\nFILE CREATED\n")
