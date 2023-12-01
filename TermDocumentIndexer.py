from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, PositionalIndex, DiskIndexWriter, DiskPositionalIndex
from text import EnglishTokenStream, NewTokenProcessor
from querying import BooleanQueryParser, DefaultRetrieval, ProbabilityRetrieval
import time
from database import get_client
import math
from queue import PriorityQueue

token_processor = NewTokenProcessor()


def index_corpus(corpus: DocumentCorpus, weight_path, db_client) -> Index:
    print("\nStarted Indexing...")
    startTime = time.time()
    document_index = PositionalIndex()
    db_client["Weights"].drop_collection("1" + weight_path[1:] if weight_path[0] == "." else weight_path)
    collection = db_client["Weights"]["1" + weight_path[1:] if weight_path[0] == "." else weight_path]
    token_count = {}
    for i in corpus:
        term_count = {}
        count = 1
        englishStream = EnglishTokenStream(i.get_content())
        token_count[i.id] = 0
        for word in englishStream:
            token_count[i.id] += 1
            for j in token_processor.normalize_type(token_processor.process_token(word)):
                document_index.add_term(j, i.id, count)
                if j in term_count:
                    term_count[j] += 1
                else:
                    term_count[j] = 1
            count += 1
        ld = 0
        for k in term_count:
            ld += ((1 + math.log(term_count[k])) ** 2)
        ld = math.sqrt(ld)
        # byte_position = file.tell()
        collection.insert_one({"doc_id": i.id, "token_count": token_count[i.id], "L_d": ld})
        # file.write(pack("d", ld))
    collection.insert_one({"docLengthA": sum(list(token_count.values()))/len(corpus), "type": "Length A"})
    endTime = time.time()
    print("\nTime take for indexing: {time:.2f} seconds".format(time=endTime - startTime))
    return document_index


def boolean_retrieval(query):
    booleanQuery = BooleanQueryParser.parse_query(query)
    postings = booleanQuery.get_postings(index, token_processor)
    if (postings is not None) and len(postings) != 0:
        return postings
    else:
        return None


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

        if str(corpus_path)[0] == "./":
            file_str = str(Path(corpus_path)) + "/" + "postings.bin"
        else:
            file_str = "./" + str(Path(corpus_path)) + "/" + "postings.bin"

        d = DirectoryCorpus.load_directory(corpus_path)
        index = DiskPositionalIndex(file_str)

    else:
        print()
        corpus_path = Path(input("Enter the path of corpus: "))
        while not corpus_path.exists():
            corpus_path = Path(
                input('\033[1;3m' + "\nEnter valid path." + '\033[0m' + "\n\nEnter the path of corpus: "))

        if str(corpus_path)[0] == "/":
            file_str = str(Path(corpus_path)) + "/" + "postings.bin"
        else:
            file_str = "./" + str(Path(corpus_path)) + "/" + "postings.bin"

        d = DirectoryCorpus.load_directory(corpus_path)
        client = get_client()
        index = index_corpus(d, file_str, client)
        client["Vocabularies"].drop_collection("1" + file_str[1:] if file_str[0] == "." else file_str)
        client.close()
        DiskIndexWriter(file_str).write_index(index)
        index = DiskPositionalIndex(file_str)

    print("\n1) Boolean Query")
    print("2) Ranked Query\n")
    boolean_ranked = int(input("Enter your choice: "))

    while boolean_ranked not in [1, 2]:
        boolean_ranked = input('\033[1;3m' + "\nEnter valid choice." + '\033[0m' + "\n\nEnter the your choice: ")

    default_probab = 0

    if boolean_ranked == 2:
        print("\n1) Default Retrieval")
        print("2) Probabilistic Retrieval\n")
        default_probab = int(input("Enter your choice: "))
        while default_probab not in [1, 2]:
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
                if default_probab == 1:
                    ret = DefaultRetrieval(file_str)
                else:
                    ret = ProbabilityRetrieval(file_str)

                scores = {}
                split_query = query.split(" ")
                wqt = 0
                for i in split_query:
                    p = index.get_postings(token_processor.normalize_type(token_processor.process_token(i))[0])
                    if p is None:
                        p = []
                        continue
                    wqt = ret.get_wqt(len(p), len(d))
                    for j in p:
                        wdt = ret.get_wdt(len(j.get_positions()), j.get_doc_id())

                        if j.get_doc_id() in scores:
                            scores[j.get_doc_id()][0] += wdt*wqt
                        else:
                            scores[j.get_doc_id()] = [wdt*wqt, wdt]

                q = PriorityQueue()
                for i in scores:
                    scores[i][0] = scores[i][0]/ret.get_Ld(i)
                    q.put((1/scores[i][0], (i, scores[i][1], scores[i][0])))

                print(f"Total number of documents are {q.qsize()}\n")
                print(f"{q.qsize()} postings for query \"{query}\"; with wQt = {wqt:.5f}")

                c = 1
                for i in range(10):
                    temp = q.get()
                    print(f"{d.get_document(temp[1][0])} = "
                          f"(wdt={temp[1][1]:.5f}, "
                          f"L_d={ret.get_Ld(temp[1][0]):.5f}, "
                          f"scores={temp[1][2]:.5f})")
                    c += 1
                    if c >= 11:
                        break
                print()
        else:
            print("Your query is empty. Input valid query.\n")

        query = input("Enter the query you wanna search: ")
        print()
    print("Hope you liked my search engine!")
