from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class FileInfo(BaseModel):
    file_id: UUID
    filename: str
    upload_time: datetime
    filesize: int


class FileInfoWithContent(BaseModel):
    file_info: FileInfo
    content: bytes
