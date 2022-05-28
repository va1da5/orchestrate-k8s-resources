import uuid

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

import jobs

app = FastAPI()


class Job(BaseModel):
    cmd: str = "echo launched; sleep 10; echo done"


@app.get("/")
def index():
    return {"status": "alive"}


@app.get("/jobs")
def get_jobs():
    return jobs.get_jobs()


@app.post("/jobs")
def create_job(job: Job):
    job_name = str(uuid.uuid4())
    return jobs.make_job(job_name=job_name, cmd=job.cmd)


@app.get("/jobs/{job_name}")
def read_job(job_name: str):
    try:
        return jobs.get_job(name=job_name)
    except jobs.JobNotFound as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc


@app.get("/jobs/{job_name}/status")
def read_job_status(job_name: str):
    try:
        return jobs.get_job(name=job_name)["status"]
    except jobs.JobNotFound as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc


@app.get("/jobs/{job_name}/logs", response_class=PlainTextResponse)
def read_pod_logs(job_name: str):
    try:
        return jobs.get_job_logs(name=job_name)
    except jobs.NoPodsFound as exc:
        raise HTTPException(status_code=404, detail="Logs not found") from exc
