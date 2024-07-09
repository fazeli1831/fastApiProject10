import multiprocessing
import time
from fastapi import FastAPI, Path
from pydantic import BaseModel
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Define a BaseModel for response
class ProcessInfo(BaseModel):
    process_name: str
    status: str

# Define your function that does the work
def myfunc(queue):
    name = multiprocessing.current_process().name
    print(f"Starting process name = {name}")
    time.sleep(2)
    print(f"Exiting process name = {name}")
    result = ProcessInfo(process_name=name, status="Process finished successfully")
    queue.put(result)

# Define your FastAPI endpoint
@app.get("/start_processes/{count}", response_model=List[ProcessInfo])
async def start_processes(count: int = Path(..., title="Number of processes to start", ge=1, le=9)):
    process_results = multiprocessing.Queue()
    processes = []

    for i in range(count):
        process = multiprocessing.Process(target=myfunc, args=(process_results,))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    results = []
    while not process_results.empty():
        results.append(process_results.get())

    return results

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
