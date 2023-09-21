from typing import Iterable
from .index import Index
from .postings import Posting


class PositionalIndex(Index):

    def __init__(self):
        self.positional_index : dict[str, list[Posting]] = dict()

    def add_term(self, term: str, documentId: int, position: int):
        if term not in self.positional_index:
            postingList = list()
            postingList.append(Posting(documentId, position))
        else:
            if self.positional_index[term][-1].doc_id != documentId:
                self.positional_index[term].append(Posting(documentId, position))
            else:
                self.positional_index[term][-1].positions.append(position)

    def get_postings(self, term: str) -> Iterable[Posting]:
        """Retrieves a sequence of Postings of documents that contain the given term."""
        if term in self.positional_index:
            return self.positional_index[term]
        else:
            return None

    def vocabulary(self) -> list[str]:
        """A (sorted) list of all terms in the index vocabulary."""
        pass