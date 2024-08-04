from fastapi import FastAPI
from worker_multiple.tasks import task1, task2
from apps_multiple.models import MockBody

app = FastAPI()

@app.post("/task1")
async def run_task1(request: MockBody):
    data = request.param
    task1.delay(data)
    return {"message": "Task 1 started"}

@app.post("/task2")
async def run_task2(request: MockBody):
    data = request.param
    task2.delay(data)
    return {"message": "Task 2 started"}