from indexing.postings import Posting
from .querycomponent import QueryComponent

class TermLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, term : str):
        self.term = term

    def get_postings(self, index, processor) -> list[Posting]:
        return index.get_postings(processor.normalize_type(processor.process_token(self.term))[0])

    def __str__(self) -> str:
        return self.term