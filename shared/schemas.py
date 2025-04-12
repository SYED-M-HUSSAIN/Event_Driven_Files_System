from pydantic import BaseModel

class FileUploadedEvent(BaseModel):
    event: str = "file.uploaded"
    file_name: str
    file_path: str

class FileValidatedEvent(BaseModel):
    event: str = "file.validated"
    file_name: str
    valid: bool

class FileInfectedEvent(BaseModel):
    event: str = "file.infected"
    file_name: str
    infected: bool

class FileIndexedEvent(BaseModel):
    event: str = "file.indexed"
    file_name: str
    metadata: dict