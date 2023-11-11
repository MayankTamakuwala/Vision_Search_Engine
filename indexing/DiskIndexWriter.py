from pymongo import MongoClient, ASCENDING
from compression.variable_byte import vb_encode


def get_client():
    CONNECTION_STRING = "mongodb://localhost:27017"

    return MongoClient(CONNECTION_STRING)


class DiskIndexWriter:

    def __init__(self, postings_path):
        self.__client = get_client()
        self.__collection = self.__client["Vocabularies"]["TermTrack"]
        self.__collection.create_index([("term", ASCENDING)],name="term_index")
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

        print("The total terms in the index are: ", len(index))
        for term in index:
            byte_position = self.postings_file.tell()

            self.add_position(term, byte_position)

            postings_list = index.get_postings(term)

            dft = len(postings_list)
            self.postings_file.write(bytes(vb_encode(dft)))

            docId_gap = 0

            for posting in postings_list:
                doc_id = posting.get_doc_id() - docId_gap
                docId_gap = posting.get_doc_id()

                self.postings_file.write(bytes(vb_encode(doc_id)))

                tftd = len(posting.get_positions())

                self.postings_file.write(bytes(vb_encode(tftd)))

                position = 0
                for p in posting.get_positions():
                    position_gap = p - position
                    position = p

                    self.postings_file.write(bytes(vb_encode(position_gap)))

        print("FILE CREATED\n")
