from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, PositionalIndex, DiskIndexWriter, DiskPositionalIndex
from text import EnglishTokenStream, NewTokenProcessor
from querying import BooleanQueryParser
import time
from indexing import get_client


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


def boolean_retrieval(query):
    booleanQuery = BooleanQueryParser.parse_query(query)
    postings = booleanQuery.get_postings(index, NewTokenProcessor())
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

        if str(corpus_path)[0] == "./":
            file_str = str(Path(corpus_path)) + "/" + "postings.bin"
        else:
            file_str = "./" + str(Path(corpus_path)) + "/" + "postings.bin"

        d = DirectoryCorpus.load_directory(corpus_path)
        index = index_corpus(d)
        client = get_client()
        client["Vocabularies"].drop_collection("1" + file_str[1:] if file_str[0] == "." else file_str)
        client.close()
        DiskIndexWriter(file_str).write_index(index)
        index = DiskPositionalIndex(file_str)

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