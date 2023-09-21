from typing import Iterable
from .index import Index
from .postings import Posting

class InvertedIndex(Index):

    def __init__(self):
        self.invertedIndex = dict()
    def add_term(self, term: str, documentId: int):
        if term not in self.invertedIndex:
            newPostingsList = list()
            newPostingsList.append(Posting(documentId))
            self.invertedIndex[term] = newPostingsList
        else:
            if(self.invertedIndex[term][-1].doc_id != documentId):
                self.invertedIndex[term].append(Posting(documentId))

    def get_postings(self, term : str) -> Iterable[Posting]:
        """Retrieves a sequence of Postings of documents that contain the given term."""
        return self.invertedIndex[term]

    def vocabulary(self) -> list[str]:
        """A (sorted) list of all terms in the index vocabulary."""
        pass