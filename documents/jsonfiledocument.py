from pathlib import Path
from typing import Iterable
from .document import Document
import json


class JSONFileDocument(Document):
    """
    Represents a document that is saved as a simple text file in the local file system.
    """
    def __init__(self, id : int, path : Path):
        super().__init__(id)
        self.path = path
        self._jsonfile = json.load(open(self.path))

    @property
    def title(self) -> str:
        return self._jsonfile["title"]

    # returns TextIOWrapper
    def get_content(self) -> Iterable[str]:
        yield self._jsonfile["body"]

    @staticmethod
    def load_from(abs_path : Path, doc_id : int) -> 'JSONFileDocument' :
        """A factory method to create a TextFileDocument around the given file path."""
        return JSONFileDocument(doc_id, abs_path)