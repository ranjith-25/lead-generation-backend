from pathlib import Path

class ProjectHelpers:
    content_types = {
        "pdf": "application/pdf",
        "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    DEFAULT_CONTENT_TYPE = "application/octet-stream"

    @classmethod
    def content_type_for(cls, filename: str | Path) -> str:
        extension = Path(filename).suffix.lower().lstrip(".")
        return cls.content_types.get(extension, cls.DEFAULT_CONTENT_TYPE)