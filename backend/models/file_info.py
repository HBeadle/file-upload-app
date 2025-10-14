from datetime import datetime
from pydantic import BaseModel


class FileInfo(BaseModel):
    filename: str
    upload_time: datetime
    filesize: int


class FileInfoWithContent(FileInfo):
    content: bytes

    @property
    def info(self) -> FileInfo:
        return FileInfo(
            filename=self.filename,
            upload_time=self.upload_time,
            filesize=self.filesize
        )
