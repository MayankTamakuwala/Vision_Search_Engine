from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, PositionalIndex, DiskIndexWriter, DiskPositionalIndex
from text import EnglishTokenStream, NewTokenProcessor
from querying import BooleanQueryParser
import time
from indexing import get_client
import uuid
import bson


def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = NewTokenProcessor()
    print("\nStarted Indexing...")
    startTime = time.time()

    document_index = PositionalIndex()
    for i in corpus:
        count = 1
        englishStream = EnglishTokenStream(i.get_content())
        for word in englishStream:
            for j in token_processor.normalize_type(token_processor.process_token(word)):
                document_index.add_term(j, i.id, count)
            count += 1
    endTime = time.time()
    print("\nTime take for indexing: {time:.2f} seconds".format(time=endTime - startTime))
    return document_index


def search_query(query: str):
    index = DiskPositionalIndex(Path("./moby.bin"))
    if query != "":
        booleanQuery = BooleanQueryParser.parse_query(query)
        postings = booleanQuery.get_postings(index, NewTokenProcessor())
        if (postings is not None) and len(postings) != 0:
            for p in postings:
                print(DirectoryCorpus.get_document(p.doc_id))
            # return postings
        else:
            return "404 Not Found. Try different query"
    else:
        return "Your query is empty. Input valid query."


def boolean_retrieval(query):
    booleanQuery = BooleanQueryParser.parse_query(query)
    postings = booleanQuery.get_postings(index, NewTokenProcessor())
    if (postings is not None) and len(postings) != 0:
        return postings
    else:
        return None


def create_index_job(corpus_path, file_path):
    corpus_path = Path(corpus_path)
    file_path = Path(file_path)

    if not corpus_path.exists():
        return [False, 0]

    if not file_path.exists():
        return [False, 0]

    jobid = uuid.uuid1()
    client = get_client()
    collection = client["IndexJobs"]["Jobs"]
    temp = collection.find_one({"jobid": bson.Binary.from_uuid(jobid)})
    while temp is not None:
        jobid = uuid.uuid1()
        temp = collection.find_one({"jobid": bson.Binary.from_uuid(jobid)})
    collection.insert_one({"jobid": bson.Binary.from_uuid(jobid), "status": "in progress"})
    client.close()

    return [True, jobid]


def create_index(jobid, corpus_path, file_path):
    client = get_client()
    collection = client["IndexJobs"]["Jobs"]

    if file_path.__str__()[0:2] != "./":
        file_path = Path("./" + file_path.__str__() + "/" + "postings.bin")
    else:
        file_path = Path(file_path.__str__() + "/" + "postings.bin")

    d = DirectoryCorpus.load_directory(corpus_path)
    index = index_corpus(d)
    client["Vocabularies"].drop_collection("TermTrack")
    DiskIndexWriter(file_path).write_index(index)
    collection.update_one(filter={"jobid": jobid}, update={"$set": {"status": "completed"}})


if __name__ == "__main__":
    print("1) Select corpus from disk")
    print("2) Build corpus on disk\n")
    corpus_on_disk = int(input("Enter your choice: "))

    while corpus_on_disk not in [1, 2]:
        # '\033[1;3m' is for bold and italic and '\033[0m' for closing tag\
        corpus_on_disk = input('\033[1;3m' + "\nEnter valid choice." + '\033[0m' + "\n\nEnter the your choice: ")

    index = None

    if corpus_on_disk == 1:
        print()
        corpus_path = Path(input("Enter the path of corpus: "))
        while not corpus_path.exists():
            corpus_path = Path(
                input('\033[1;3m' + "\nEnter valid path."
                      + '\033[0m' + "\n\nEnter the path of corpus: "))

        file_path = Path(input("Enter the path of directory where postings.bin is saved: "))
        while not file_path.exists():
            file_path = Path(
                input('\033[1;3m' + "\nEnter valid path."
                      + '\033[0m' + "\n\nEnter the path of directory where postings.bin is saved: "))

        if file_path.__str__()[0:2] != "./":
            file_path = Path("./" + file_path.__str__() + "/" + "postings.bin")
        else:
            file_path = Path(file_path.__str__() + "/" + "postings.bin")

        d = DirectoryCorpus.load_directory(corpus_path)
        index = DiskPositionalIndex(file_path)

    else:
        print()
        corpus_path = Path(input("Enter the path of corpus: "))
        while not corpus_path.exists():
            corpus_path = Path(
                input('\033[1;3m' + "\nEnter valid path." + '\033[0m' + "\n\nEnter the path of corpus: "))

        file_path = Path(input("Enter the path you wanna save your file to: "))
        while not file_path.exists():
            corpus_path = Path(
                input(
                    '\033[1;3m' + "\nEnter valid path." + '\033[0m' + "\n\nEnter the path you wanna save to file to: "))

        if file_path.__str__()[0:2] != "./":
            file_path = Path("./" + file_path.__str__() + "/" + "postings.bin")
        else:
            file_path = Path(file_path.__str__() + "/" + "postings.bin")

        d = DirectoryCorpus.load_directory(corpus_path)
        index = index_corpus(d)
        client = get_client()
        client["Vocabularies"].drop_collection("TermTrack")
        client.close()
        diskIndexWriter = DiskIndexWriter(file_path).write_index(index)
        index = DiskPositionalIndex(file_path)

    print("\n1) Boolean Query")
    print("2) Ranked Query\n")
    boolean_ranked = int(input("Enter your choice: "))

    while boolean_ranked not in [1, 2]:
        boolean_ranked = input('\033[1;3m' + "\nEnter valid choice." + '\033[0m' + "\n\nEnter the your choice: ")

    print("\n\nType exit() to quit the search engine.\n")
    query = input("Enter the query you wanna search: ")
    print()

    while query != "exit()":
        if query != "":
            if boolean_ranked == 1:
                postings = boolean_retrieval(query)
                if postings is not None:
                    for p in postings:
                        print(d.get_document(p.doc_id))
                    print()
                    print("Postings for", '\033[1;3m' + query + '\033[0m',
                          "is in" if len(postings) == 1 else "are in",
                          '\033[1;3m' + str(len(postings)) + '\033[0m',
                          "document\n" if len(postings) == 1 else "documents\n")
                else:
                    print("Postings not found for", '\033[1;3m' + query + '\033[0m', "\n")

            else:
                print("Ranked Retrival in progress...")
        else:
            print("Your query is empty. Input valid query.\n")

        query = input("Enter the query you wanna search: ")
        print()
    print("Hope you liked my search engine!")