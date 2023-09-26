class Posting:
    """A Posting encapulates a document ID associated with a search query component."""


    def __init__(self, doc_id : int, positionNum: int = None, positionList: list[int] = None):
        self.doc_id = doc_id
        if positionList is None and positionNum is not None:
            self.positions = [positionNum]
        elif positionNum is None and positionList is not None:
            self.positions = positionList
        else:
            self.positions = []

    def get_doc_id(self) -> int:
        return self.doc_id

    def get_positions(self) -> list[int]:
        return self.positions