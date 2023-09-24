from .querycomponent import QueryComponent
from indexing import Index, Posting

from querying import querycomponent 

class OrQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        self.components = components

    def get_postings(self, index : Index) -> list[Posting]:
        result = []
        # TODO: program the merge for an OrQuery, by gathering the postings of the composed QueryComponents and
        #  merging the resulting postings.
        mergeDict = {}
        temp = []
        for i in self.components:
            temp.append(i.get_postings(index))

        noneCount = temp.count(None)

        for _ in range(noneCount):
            temp.remove(None)

        for i in temp:
            for j in i:
                if (len(mergeDict) == 0) or (j.get_doc_id() not in mergeDict):
                    mergeDict[j.get_doc_id()] = j.get_positions()
                else:
                    mergeDict[j.get_doc_id()].extend(j.get_positions())
                    mergeDict[j.get_doc_id()] = list(set(mergeDict[j.get_doc_id()]))

        for i in mergeDict:
            result.append(Posting(i, positionList=mergeDict[i]))

        return result

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"