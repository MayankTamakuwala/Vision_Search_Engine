from .querycomponent import QueryComponent
from indexing import Index, Posting
from copy import deepcopy

class OrQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        self.components = components

    def get_postings(self, index : Index, processor) -> list[Posting]:
        # TODO: program the merge for an OrQuery, by gathering the postings of the composed QueryComponents and
        #  merging the resulting postings.
        temp = []
        for i in self.components:
            temp.append(i.get_postings(index, processor))

        for _ in range(temp.count(None)):
            temp.remove(None)

        p1 = temp[0]
        postingTrack = 1
        while postingTrack<len(temp):
            p2 = temp[postingTrack]
            pointer1 = 0
            pointer2 = 0
            mergeList = []
            while pointer1 < len(p1) and pointer2 < len(p2):
                if p1[pointer1].get_doc_id() < p2[pointer2].get_doc_id():
                    mergeList.append(Posting(p1[pointer1].get_doc_id()))
                    pointer1 += 1

                elif p2[pointer2].get_doc_id() < p1[pointer1].get_doc_id():
                    mergeList.append(Posting(p2[pointer2].get_doc_id()))
                    pointer2 += 1

                else:
                    mergeList.append(Posting(p1[pointer1].get_doc_id()))
                    pointer1 += 1
                    pointer2 += 1

            while pointer1<len(p1):
                mergeList.append(Posting(p1[pointer1].get_doc_id()))
                pointer1 += 1

            while pointer2<len(p2):
                mergeList.append(Posting(p2[pointer2].get_doc_id()))
                pointer2 += 1

            p1 = deepcopy(mergeList)
            postingTrack += 1

        result = deepcopy(p1)
        return result

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"