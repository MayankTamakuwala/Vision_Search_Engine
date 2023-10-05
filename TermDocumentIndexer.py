from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, TermDocumentIndex, InvertedIndex, PositionalIndex
from text import BasicTokenProcessor, EnglishTokenStream, NewTokenProcessor
from querying import BooleanQueryParser
import os

"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""


def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = NewTokenProcessor()
    # vocabulary = set()

    # for d in corpus:
    #     englishStream = EnglishTokenStream(d.get_content())
    #     for word in englishStream:
    #         vocabulary.add(token_processor.process_token(word))
        # TODO:
        #   Tokenize the document's content by creating an EnglishTokenStream around the document's .content()
        #   Iterate through the token stream, processing each with token_processor's process_token method.
        #   Add the processed token (a "term") to the vocabulary set.

    document_index = PositionalIndex()
    for i in corpus:
        count = 0
        englishStream = EnglishTokenStream(i.get_content())
        for word in englishStream:
            for j in token_processor.normalize_type(token_processor.process_token(word)):
                document_index.add_term(j, i.id, count)
            count += 1

    return document_index

    # TODO:
    #   After the above, next:
    #   Create a TermDocumentIndex object, with the vocabulary you found, and the len() of the corpus.
    #   Iterate through the documents in the corpus:
    #   Tokenize each document's content, again.
    #   Process each token.
    #   Add each processed term to the index with .add_term().


if __name__ == "__main__":
    corpus_path = Path(input("Enter the path of corpus: "))
    while not corpus_path.exists():
        # '\033[1;3m' is for bold and italic and '\033[0m' for closing tag
        corpus_path = Path(input('\033[1;3m' + "\nEnter valid path." + '\033[0m' + "\n\nEnter the path of corpus: "))
    d = DirectoryCorpus.load_directory(corpus_path)

    # ----------------------------------------------------------------------------------------------------------------------
    # file_list = [f for f in os.listdir(corpus_path) if os.path.isfile(f)]
    # for i in file_list:
    #     if ".pdf" in i:
    #         d = DirectoryCorpus.load_directory(corpus_path, ".pdf")
    #     elif ".txt" in i:
    #         d = DirectoryCorpus.load_directory(corpus_path, ".txt")
    # TODO: Send the list of Directory Corpus to index_corpus() function and loop thru every object to make just ONE index
    # ----------------------------------------------------------------------------------------------------------------------

    index = index_corpus(d)
    print("Type exit() to quit the search engine.\n")
    query = input("Enter the query you wanna search: ")
    print()
    while query!="exit()":
        if query != "":
            booleanQuery = BooleanQueryParser.parse_query(query)
            postings = booleanQuery.get_postings(index, NewTokenProcessor())
            if (postings is not None) and len(postings) != 0:
                for p in postings:
                    print(d.get_document(p.doc_id))
                print()
                print("Postings for", '\033[1;3m' + query + '\033[0m', "are in" , '\033[1;3m' + str(len(postings)) + '\033[0m', "documents\n")
            else :
                print("Postings not found for", '\033[1;3m' + query + '\033[0m', "\n")
        else:
            print("Your query is empty. Input valid query.\n")

        query = input("Enter the query you wanna search: ")
        print()
    print("Hope you liked my search engine!")