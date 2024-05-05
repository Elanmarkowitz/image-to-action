import uuid
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
import image_action_agent
import traceback

import logging 

logging.basicConfig(level=logging.INFO)

app = FastAPI()

processing_tasks = {}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload/")
async def upload_image_and_text(file: UploadFile = File(...), text: str = Form(...), background_tasks: BackgroundTasks = None):
    try:
        # Save the uploaded image locally
        with open(file.filename, "wb") as image:
            image.write(file.file.read())
        
        # Generate unique ID for this processing task
        task_id = str(uuid.uuid4())
        
        # Store the task ID with initial status
        processing_tasks[task_id] = {"status": "processing"}

        # Run processing task in the background
        background_tasks.add_task(run_agent, task_id, file, text)
        
        return {"task_id": task_id, "status": "processing"}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
def run_agent(task_id, file, text):
    try:
        processing_tasks[task_id] = {"status": "running", "command_history": []}
        command_results, final_status = image_action_agent.run_agent(file.filename, text, processing_tasks[task_id]["command_history"])
        processing_tasks[task_id] = {"status": "completed", "command_results": command_results, "final_status": final_status}
    except Exception as e:
        logging.info(traceback.format_exc())
        processing_tasks[task_id].update({"status": "error", "error": str(e)})

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    if task_id in processing_tasks:
        return processing_tasks[task_id]
    else:
        return {"status": "not found"}
    
logging.info("Server started.")