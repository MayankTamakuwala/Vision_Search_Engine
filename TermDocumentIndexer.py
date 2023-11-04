from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, TermDocumentIndex, InvertedIndex, PositionalIndex, DiskIndexWriter, DiskPositionalIndex
from text import BasicTokenProcessor, EnglishTokenStream, NewTokenProcessor
from querying import BooleanQueryParser
import os
import time
from pymongo import MongoClient
from indexing import get_client
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException

"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""


def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = NewTokenProcessor()
    print("\nStarted Indexing...")
    startTime = time.time()
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
        count = 1
        englishStream = EnglishTokenStream(i.get_content())
        for word in englishStream:
            for j in token_processor.normalize_type(token_processor.process_token(word)):
                document_index.add_term(j, i.id, count)
            count += 1
    endTime = time.time()
    print("\nTime take for indexing: {time:.2f} seconds".format(time=endTime - startTime))
    return document_index

    # TODO:
    #   After the above, next:
    #   Create a TermDocumentIndex object, with the vocabulary you found, and the len() of the corpus.
    #   Iterate through the documents in the corpus:
    #   Tokenize each document's content, again.
    #   Process each token.
    #   Add each processed term to the index with .add_term().


if __name__ == "__main__":
    print("1) Does the corpus exists on disk?")
    print("2) Do you want to make corpus on disk?\n")
    corpus_on_disk = int(input("Enter your choice: "))

    while corpus_on_disk not in [1, 2]:
        # '\033[1;3m' is for bold and italic and '\033[0m' for closing tag\
        corpus_on_disk = Path(input('\033[1;3m' + "\nEnter valid choice." + '\033[0m' + "\n\nEnter the your choice: "))

    index = None

    if corpus_on_disk == 1:
        print()
        corpus_path = Path(input(
            '\033[1;3m' + "Include the binary file name in the path" + '\033[0m' + "\n\nEnter the path of corpus: "))
        while not corpus_path.exists() and corpus_path.__str__().count(".bin") <= 0:
            corpus_path = Path(
                input('\033[1;3m' + "\nEnter valid path.\n\nInclude the binary file name in the path"
                      + '\033[0m' + "\n\nEnter the path of corpus: "))

        index = DiskPositionalIndex(corpus_path)

    else:
        print()
        corpus_path = Path(input("Enter the path of corpus: "))
        while not corpus_path.exists():
            corpus_path = Path(
                input('\033[1;3m' + "\nEnter valid path." + '\033[0m' + "\n\nEnter the path of corpus: "))

        file_name = input("Enter the file name you wanna create: ")
        while file_name == "" or (not file_name.isalnum()):
            file_name = input('\033[1;3m' + "\nEnter valid file name." + '\033[0m' + "\n\nEnter the file name you "
                                                                                     "wanna create: ")
        file_path = Path(input("Enter the path you wanna save your file to:"))
        while not file_path.exists():
            corpus_path = Path(
                input(
                    '\033[1;3m' + "\nEnter valid path." + '\033[0m' + "\n\nEnter the path you wanna save to file to: "))

        if file_path.__str__()[0:2] != "./":
            file_path = Path("./" + file_path.__str__() + "/" + file_name + ".bin")
        else:
            file_path = Path(file_path.__str__() + "/" + file_name + ".bin")

        d = DirectoryCorpus.load_directory(corpus_path)
        index = index_corpus(d)
        client = get_client()
        client["Vocabularies"].drop_collection("TermTrack")
        client.close()
        diskIndexWriter = DiskIndexWriter(file_path).write_index(index)
        index = DiskPositionalIndex(file_path)

    print("Type exit() to quit the search engine.\n")
    query = input("Enter the query you wanna search: ")
    print()

    while query != "exit()":
        if query != "":
            booleanQuery = BooleanQueryParser.parse_query(query)
            postings = booleanQuery.get_postings(index, NewTokenProcessor())
            if (postings is not None) and len(postings) != 0:
                for p in postings:
                    print(d.get_document(p.doc_id))
                print()
                if len(postings) == 1:
                    print("Postings for", '\033[1;3m' + query + '\033[0m', "are in",
                          '\033[1;3m' + "1" + '\033[0m', "documents\n")
                else:
                    print("Postings for", '\033[1;3m' + query + '\033[0m', "are in",
                          '\033[1;3m' + str(len(postings)) + '\033[0m', "documents\n")
            else:
                print("Postings not found for", '\033[1;3m' + query + '\033[0m', "\n")
        else:
            print("Your query is empty. Input valid query.\n")

        query = input("Enter the query you wanna search: ")
        print()
    print("Hope you liked my search engine!")
