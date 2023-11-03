from pathlib import Path
from typing import Iterable
from .document import Document
from PyPDF2 import PdfReader
class PDFFileDocument(Document):
    """
    Represents a document that is saved as a simple PDF file in the local file system.
    """
    def __init__(self, id : int, path : Path):
        super().__init__(id)
        self.path = path
        self._pdf = PdfReader(self.path)

    @property
    def title(self) -> str:
        return self.path.stem

    # returns StringIOWrapper
    def get_content(self) -> Iterable[str]:
        for i in self._pdf.pages:
            yield i.extract_text()

    @staticmethod
    def load_from(abs_path : Path, doc_id : int) -> 'PDFFileDocument' :
        """A factory method to create a TextFileDocument around the given file path."""
        return PDFFileDocument(doc_id, abs_path)