from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexing import Index, PositionalIndex, DiskIndexWriter, DiskPositionalIndex
from text import EnglishTokenStream, NewTokenProcessor
from querying import BooleanQueryParser, DefaultRetrieval, ProbabilityRetrieval
import time
from database import get_client
import uuid
import bson
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
        collection.insert_one({"doc_id": i.id, "token_count": token_count[i.id], "L_d": ld})
    collection.insert_one({"docLengthA": sum(list(token_count.values()))/len(corpus), "type": "Length A"})
    endTime = time.time()
    print("\nTime take for indexing: {time:.2f} seconds".format(time=endTime - startTime))
    return document_index


def boolean_retrieval(corpus_path, file_path, query):
    if not Path(file_path).exists():
        return [False, 0]
    if not Path(corpus_path).exists():
        return [True, 0]
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
    client = get_client()
    index = index_corpus(d, file_str, client)
    client["Vocabularies"].drop_collection("1" + file_str[1:] if file_str[0] == "." else file_str)
    DiskIndexWriter(file_str).write_index(index)
    collection.update_one(filter={"jobid": jobid}, update={"$set": {"status": "completed", "corpus_path": corpus_str,
                                                                    "file_name": file_name}})


def ranked_retrieval(corpus_path, file_path, query, default_probab):
    if not Path(file_path).exists():
        return [False, 0]
    if not Path(corpus_path).exists():
        return [True, 0]

    if default_probab:
        ret = DefaultRetrieval(file_path)
    else:
        ret = ProbabilityRetrieval(file_path)

    d = DirectoryCorpus.load_directory(corpus_path)
    index = DiskPositionalIndex(file_path)
    scores = {}
    split_query = query.split(" ")
    for i in split_query:
        p = index.get_postings(token_processor.normalize_type(token_processor.process_token(i))[0])
        if p is None:
            continue
        wqt = ret.get_wqt(len(p), len(d))
        for j in p:
            wdt = ret.get_wdt(len(j.get_positions()), j.get_doc_id())

            if j.get_doc_id() in scores:
                scores[j.get_doc_id()][0] += wdt * wqt
            else:
                scores[j.get_doc_id()] = [wdt * wqt, wdt]

    q = PriorityQueue()
    for i in scores:
        scores[i][0] = scores[i][0] / ret.get_Ld(i)
        q.put((1 / scores[i][0], (i, scores[i][1], scores[i][0])))

    if q.qsize() == 0:
        return None
    return [q, d]
