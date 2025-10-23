from datetime import datetime
from fastapi import UploadFile
from typing import Tuple
from uuid import uuid4

from models.file_info import FileInfo, FileInfoWithContent

import exceptions
import io
import os

VALID_FILE_EXTENSIONS = (
    ".pdf",
    ".csv",
    ".txt"
)

async def parse_file(
    file: UploadFile, 
    chunk_size: int = 1024 * 1024
) -> FileInfoWithContent:
    filename = file.filename
    valid, extension = _valid_filetype(filename)
    if not valid:
        raise exceptions.FileTypeNotPermitted(
            f"File extension must be one of {', '.join(VALID_FILE_EXTENSIONS)} " 
            f"(got: {extension})."
        )
    
    upload_time = datetime.now()

    with io.BytesIO() as buffer:
        # Simulate streaming to handle large files 
        # (in prod, these chunks would be stored to disk/cloud)
        while chunk := await file.read(chunk_size):
            buffer.write(chunk)
        content = buffer.getvalue()

    file_info = FileInfo(
        file_id=uuid4(),
        filename=filename,
        upload_time=upload_time,
        filesize=len(content)
    )
    
    return FileInfoWithContent(
        file_info=file_info,
        content=content
    )


def _valid_filetype(filename: str) -> Tuple[bool, str]:
    extension = _get_file_extension(filename)
    if extension not in VALID_FILE_EXTENSIONS:
        return False, extension
    return True, extension
    

def _get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()
