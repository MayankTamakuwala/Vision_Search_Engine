from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, BackgroundTasks
from database import get_client
from api_helper import create_index_job, create_index, boolean_retrieval, ranked_retrieval
import bson
from uuid import UUID

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/create-index")
async def indexing(prompt: dict, background_tasks: BackgroundTasks):
    if ("corpus_path" in prompt) and ("file_name" in prompt) and ("job_name" in prompt):
        job = create_index_job(prompt["corpus_path"], prompt["job_name"])
        if not job[0]:
            if job[1] == 1:
                raise HTTPException(400, f"job_name already exists")
            raise HTTPException(400, f"Invalid corpus_path, file_name or job_name")
        else:
            background_tasks.add_task(create_index, bson.Binary.from_uuid(job[1]),
                                      prompt["corpus_path"], prompt["file_name"])
            return {"job_name": prompt["job_name"], "jobid": job[1], "status": "in progress"}

    else:
        raise HTTPException(400, f"Invalid request. Your request should include required "
                                 f"fields corpus_path, file_name AND job_name")


@app.get("/check-status")
def status(prompt: dict):
    if "jobid" in prompt:
        c = get_client()
        collection = c["IndexJobs"]["Jobs"]
        prompt["jobid"] = UUID(prompt["jobid"])
        temp = collection.find_one({"jobid": bson.Binary.from_uuid(prompt["jobid"])}, {"_id": False})
        if temp is None:
            raise HTTPException(404, f"Job ID does not exists")
        else:
            c.close()
            temp["jobid"] = UUID(bytes=temp["jobid"])
            return temp

    elif "job_name" in prompt:
        c = get_client()
        collection = c["IndexJobs"]["Jobs"]
        temp = collection.find_one({"job_name": prompt["job_name"]}, {"_id": False})
        temp["jobid"] = UUID(bytes=temp["jobid"])
        if temp is None:
            raise HTTPException(404, f"Job Name does not exists")
        else:
            c.close()
            return temp
    else:
        raise HTTPException(400, f"Invalid request. Your request should include required field jobid or job_name.")


def boolean_retrieval_helper(temp, prompt, using_field):
    if temp is None:
        raise HTTPException(404, f"{using_field} does not exists")
    if temp["status"] == "in progress":
        raise HTTPException(403, f"Index built is still in progress")
    result = boolean_retrieval(temp["corpus_path"], temp["corpus_path"] + "/" + temp["file_name"] + ".bin",
                               prompt["query"])
    if result[0] == False:
        raise HTTPException(404, "File " + temp["file_name"] + ".bin does not exist on path " + temp["corpus_path"])
    elif result[0] == True:
        raise HTTPException(404, "Corpus does not exist on path " + temp["corpus_path"])
    if result is None:
        raise HTTPException(404, "No postings found for the query")
    else:
        res = []
        for i in result[0]:
            res.append(str(result[1].get_document(i.doc_id)))
        return {"posting_count": len(result[0]), "docs": res}


@app.get("/boolean-retrieval")
def bool_ret(prompt: dict):
    if ("job_name" in prompt) and ("query" in prompt):
        client = get_client()
        job_collection = client["IndexJobs"]["Jobs"]
        temp = job_collection.find_one({"job_name": prompt["job_name"]})
        return boolean_retrieval_helper(temp, prompt, "Job Name")

    elif ("jobid" in prompt) and ("query" in prompt):
        client = get_client()
        job_collection = client["IndexJobs"]["Jobs"]
        prompt["jobid"] = UUID(prompt["jobid"])
        temp = job_collection.find_one({"jobid": bson.Binary.from_uuid(prompt["jobid"])})
        return boolean_retrieval_helper(temp, prompt, "Job ID")

    else:
        raise HTTPException(400, f"Invalid request. Your request should include required fields "
                                 f"query and either jobid or job_name.")


def ranked_retrieval_helper(temp, prompt, using_field, default_probab):
    if temp is None:
        raise HTTPException(404, f"{using_field} does not exists")
    if temp["status"] == "in progress":
        raise HTTPException(403, f"Index built is still in progress")
    result = ranked_retrieval(temp["corpus_path"], temp["corpus_path"] + "/" + temp["file_name"] + ".bin",
                               prompt["query"], default_probab)
    if result[0] == False:
        raise HTTPException(404, "File " + temp["file_name"] + ".bin does not exist on path " + temp["corpus_path"])
    elif result[0] == True:
        raise HTTPException(404, "Corpus does not exist on path " + temp["corpus_path"])
    if result is None:
        raise HTTPException(404, "No postings found for the query")
    else:
        total_size = result[0].qsize()
        res = []

        if result[0].qsize() < 10:
            for i in range(result[0].qsize()):
                top_item = result[0].get()
                res.append((result[1].get_document(top_item[1][0]).title, top_item[1][2]))
        else:
            c = 1
            for i in range(10):
                top_item = result[0].get()
                res.append((result[1].get_document(top_item[1][0]).title, top_item[1][2]))
                c += 1
                if c >= 11:
                    break
        return {"posting_count": total_size, "top_ten_docs_with_scores": res}


@app.get("/default-ranked-retrieval")
def def_ranked_ret(prompt: dict):
    if ("job_name" in prompt) and ("query" in prompt):
        client = get_client()
        job_collection = client["IndexJobs"]["Jobs"]
        temp = job_collection.find_one({"job_name": prompt["job_name"]})
        return ranked_retrieval_helper(temp, prompt, "Job Name", True)

    elif ("jobid" in prompt) and ("query" in prompt):
        client = get_client()
        job_collection = client["IndexJobs"]["Jobs"]
        prompt["jobid"] = UUID(prompt["jobid"])
        temp = job_collection.find_one({"jobid": bson.Binary.from_uuid(prompt["jobid"])})
        return ranked_retrieval_helper(temp, prompt, "Job ID", True)

    else:
        raise HTTPException(400, f"Invalid request. Your request should include required fields "
                                 f"query and either jobid or job_name.")


@app.get("/probability-ranked-retrieval")
def pro_ranked_ret(prompt: dict):
    if ("job_name" in prompt) and ("query" in prompt):
        client = get_client()
        job_collection = client["IndexJobs"]["Jobs"]
        temp = job_collection.find_one({"job_name": prompt["job_name"]})
        return ranked_retrieval_helper(temp, prompt, "Job Name", False)

    elif ("jobid" in prompt) and ("query" in prompt):
        client = get_client()
        job_collection = client["IndexJobs"]["Jobs"]
        prompt["jobid"] = UUID(prompt["jobid"])
        temp = job_collection.find_one({"jobid": bson.Binary.from_uuid(prompt["jobid"])})
        return ranked_retrieval_helper(temp, prompt, "Job ID", False)

    else:
        raise HTTPException(400, f"Invalid request. Your request should include required fields "
                                 f"query and either jobid or job_name.")
