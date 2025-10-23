from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from uuid import UUID

from logic.parse_file import parse_file
from models.file_info import FileInfo, FileInfoWithContent
import exceptions

import os

app = FastAPI(title="File Upload Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.environ["FRONTEND_URL"],
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uploaded_files: Dict[UUID, FileInfoWithContent] = {}

@app.get("/")
def index() -> str:
    return "File Upload server is operational."


@app.get("/api/v1/files")
def get_files() -> Dict[str, List[FileInfo]]:
    return {"files": [f.file_info for f in uploaded_files.values()]}


@app.post("/api/v1/files")
async def upload_file(file: UploadFile = File(...)) -> FileInfo:
    try:
        parsed_file = await parse_file(file)
        file_info = parsed_file.file_info
        uploaded_files[file_info.file_id] = parsed_file
        return file_info
    except exceptions.FileTypeNotPermitted as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Bad file type.",
                "message": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Unexpected server error.",
                "message": str(e)
            }
        )


@app.delete("/api/v1/files/{file_id}")
def delete_file(file_id: str) -> Dict:
    file_id = UUID(file_id)
    if file_id not in uploaded_files:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "File not found.",
                "message": f"File with ID {file_id} does not exist."
            }
        )
    
    file_content = uploaded_files.pop(file_id)
    return {
        "content": file_content.file_info.model_dump(), 
        "message": f"File {file_content.file_info.filename} deleted successfully"
    }
