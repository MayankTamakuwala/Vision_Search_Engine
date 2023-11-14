from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, BackgroundTasks
from indexing import get_client
from api_helper import create_index_job, create_index
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
    if ("corpus_path" in prompt) and ("index_path" in prompt):
        job = create_index_job(prompt["corpus_path"], prompt["index_path"])
        if not job[0]:
            raise HTTPException(405, f"Invalid corpus_path or index_path")
        else:
            background_tasks.add_task(create_index, bson.Binary.from_uuid(job[1]), prompt["corpus_path"], prompt["index_path"])
            return {"jobid": job[1], "status": "in progress"}

    else:
        raise HTTPException(405, f"Invalid request. Your request should include required fields corpus_path, index_path.")


@app.get("/check-status")
async def indexing(prompt: dict):
    if "jobid" in prompt:
        c = get_client()
        collection = c["IndexJobs"]["Jobs"]
        prompt["jobid"] = UUID(prompt["jobid"])
        temp = collection.find_one({"jobid": bson.Binary.from_uuid(prompt["jobid"])})
        jobid = UUID(bytes=temp["jobid"])
        if temp is None:
            raise HTTPException(404, f"Job Id does not exists")
        else:
            return {"jobid": jobid, "status": temp["status"]}
    else:
        raise HTTPException(405, f"Invalid request. Your request should include required field jobid.")
