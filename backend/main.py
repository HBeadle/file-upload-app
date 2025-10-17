# 6. Add README.md

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List

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

uploaded_files: Dict[str, FileInfoWithContent] = {}

@app.get("/")
def index() -> str:
    return "File Upload server is operational."


@app.get("/api/v1/files")
def get_files() -> Dict[str, List[FileInfo]]:
    return {"files": [f.info for f in uploaded_files.values()]}


@app.post("/api/v1/files")
async def upload_file(file: UploadFile = File(...)) -> FileInfo:
    # Do not allow duplicate uploads (user must delete on frontend first)
    filename = file.filename
    if filename in uploaded_files:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File already uploaded.",
                "message": f"File {filename} has already been uploaded."
            }
        )
    
    try:
        file_info = await parse_file(file)
        uploaded_files[file_info.filename] = file_info
        return file_info.info
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
                "message": {str(e)}
            }
        )


@app.delete("/api/v1/files/{filename}")
def delete_file(filename: str) -> Dict[str, str]:
    if filename not in uploaded_files:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "File not found.",
                "message": f"File {filename} does not exist."
            }
        )
    
    del uploaded_files[filename]
    return {"message": f"File {filename} deleted successfully"}
    