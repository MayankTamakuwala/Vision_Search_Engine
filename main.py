from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test/")
async def test_api(prompt: dict):
    if "name" in prompt:
        return prompt["name"]
    else:
        raise HTTPException(404, f"Invalid Request")


@app.get("/")
async def help_api():
    return {
        "Use same corpus on disk": ""
    }
