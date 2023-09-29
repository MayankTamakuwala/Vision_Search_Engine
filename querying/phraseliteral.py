from indexing.postings import Posting
from .querycomponent import QueryComponent
from copy import deepcopy

class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms : list[QueryComponent]):
        self.literals = terms

    def get_postings(self, index, processor) -> list[Posting]:
        temp = []
        for i in self.literals:
            temp.append(i.get_postings(index, processor))

        for _ in range(temp.count(None)):
            temp.remove(None)

        if len(temp) > 0:
            p1 = temp[0]
            postingTrack = 1
            while postingTrack < len(temp):
                p2 = temp[postingTrack]
                pointer1 = 0
                pointer2 = 0
                mergeList = []
                while pointer1 < len(p1) and pointer2 < len(p2):
                    if p1[pointer1].get_doc_id() < p2[pointer2].get_doc_id():
                        pointer1 += 1

                    elif p2[pointer2].get_doc_id() < p1[pointer1].get_doc_id():
                        pointer2 += 1

                    else:
                        positionPointer1 = 0
                        positionPointer2 = 0
                        p1Positions = p1[pointer1].get_positions()
                        p2Positions = p2[pointer2].get_positions()
                        mergedPostings = []
                        while positionPointer1 < len(p1Positions) and positionPointer2 < len(p2Positions):
                            if p1Positions[positionPointer1] == p2Positions[positionPointer2] - 1:
                                mergedPostings.append(p2Positions[positionPointer2])
                            positionPointer1 += 1
                            positionPointer2 += 1

                        if len(mergedPostings) > 0:
                            mergeList.append(Posting(p1[pointer1].get_doc_id(), positionList=mergedPostings))

                        pointer2 += 1
                        pointer1 += 1

                p1 = deepcopy(mergeList)
                postingTrack += 1

            cutDownValue = len(self.literals) - 1
            if len(p1) > 0:
                for i in p1:
                    for j in range(len(i.positions)):
                        i.positions[j] -= cutDownValue

            return p1
        return []
        # TODO: program this method. Retrieve the postings for the individual literals in the phrase,
        #  and positional merge them together.

    def __str__(self) -> str:
        return '"' + " ".join(map(str, self.literals)) + '"'