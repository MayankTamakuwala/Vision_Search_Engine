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


def boolean_retrieval(corpus_path, file_path, query):
    if not Path(file_path).exists():
        return [False, 0, 0]
    d = DirectoryCorpus.load_directory(corpus_path)
    index = DiskPositionalIndex(file_path)
    booleanQuery = BooleanQueryParser.parse_query(query)
    postings = booleanQuery.get_postings(index, NewTokenProcessor())
    if (postings is not None) and len(postings) != 0:
        return [postings, d]
    else:
        return None


def create_index_job(corpus_path, job_name):
    corpus_path = Path(corpus_path)

    if not corpus_path.exists():
        return [False, 0]

    jobid = uuid.uuid1()
    client = get_client()
    collection = client["IndexJobs"]["Jobs"]
    temp = collection.find_one({"job_name": job_name})

    if temp is not None:
        return [False, 1]

    temp = collection.find_one({"jobid": bson.Binary.from_uuid(jobid)})
    while temp is not None:
        jobid = uuid.uuid1()
        temp = collection.find_one({"jobid": bson.Binary.from_uuid(jobid)})
    collection.insert_one({"job_name": job_name, "jobid": bson.Binary.from_uuid(jobid), "status": "in progress"})
    client.close()

    return [True, jobid]


def create_index(jobid, corpus_path, file_name):
    corpus_str = corpus_path
    corpus_path = Path(corpus_path)

    client = get_client()
    collection = client["IndexJobs"]["Jobs"]

    if str(Path(corpus_path))[0] == "/":
        file_str = str(Path(corpus_path)) + "/" + file_name + ".bin"
    else:
        file_str = "./" + str(Path(corpus_path)) + "/" + file_name + ".bin"

    d = DirectoryCorpus.load_directory(corpus_path)
    index = index_corpus(d)
    client["Vocabularies"].drop_collection("1" + file_str[1:] if file_str[0] == "." else file_str)
    DiskIndexWriter(file_str).write_index(index)
    collection.update_one(filter={"jobid": jobid}, update={"$set": {"status": "completed", "corpus_path": corpus_str,
                                                                    "file_name": file_name}})


# if __name__ == "__main__":
#     boolean_retrieval("./corpus", "./corpus", "postings")
