from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, TermDocumentIndex, InvertedIndex, PositionalIndex
from text import BasicTokenProcessor, EnglishTokenStream, NewTokenProcessor

"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""


def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = BasicTokenProcessor()
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
            document_index.add_term(token_processor.process_token(word), i.id, count)
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
    corpus_path = Path()
    d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(d)
    # We aren't ready to use a full query parser;
    # for now, we'll only support single-term queries.
    print("Type exit() to quit the search engine.\n")
    query = input("Enter the query you wanna search: ")
    print()
    while query!="exit()":
        for p in index.get_postings(query):
            print(d.get_document(p.doc_id))
        print()
        query = input("Enter the query you wanna search: ")
        print()
    print("Hope you liked my search engine!")

    # TODO: fix this application so the user is asked for a term to search.