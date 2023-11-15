from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, BackgroundTasks
from indexing import get_client
from api_helper import create_index_job, create_index, boolean_retrieval
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
        temp = collection.find_one({"jobid": bson.Binary.from_uuid(prompt["jobid"])})
        jobid = UUID(bytes=temp["jobid"])
        if temp is None:
            raise HTTPException(404, f"Job ID does not exists")
        else:
            c.close()
            return {"job_name": temp["job_name"], "jobid": jobid, "status": temp["status"],
                    "corpus_path": temp["corpus_path"], "file_name": temp["file_name"]}

    elif "job_name" in prompt:
        c = get_client()
        collection = c["IndexJobs"]["Jobs"]
        temp = collection.find_one({"job_name": prompt["job_name"]})
        if temp is None:
            raise HTTPException(404, f"Job Name does not exists")
        else:
            c.close()
            return {"job_name": temp["job_name"], "jobid": UUID(bytes=temp["jobid"]),
                    "status": temp["status"], "corpus_path": temp["corpus_path"], "file_name": temp["file_name"]}
    else:
        raise HTTPException(400, f"Invalid request. Your request should include required field jobid or job_name.")


def boolean_retrieval_helper(temp, prompt, using_field):
    if temp["status"] == "in progress":
        raise HTTPException(403, f"Index built is still in progress")
    if temp is None:
        raise HTTPException(404, f"{using_field} does not exists")
    result = boolean_retrieval(temp["corpus_path"], temp["corpus_path"] + "/" + temp["file_name"] + ".bin",
                               prompt["query"])
    if not result[0]:
        raise HTTPException(404, "File " + temp["file_name"] + ".bin does not exist on path " + temp["corpus_path"])
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
