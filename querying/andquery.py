from .querycomponent import QueryComponent
from indexing import Index, Posting
from copy import deepcopy


class AndQuery(QueryComponent):
    def __init__(self, components: list[QueryComponent]):
        # please don't rename the "components" field.
        self.components = components

    def get_postings(self, index: Index, processor) -> list[Posting]:
        # TODO: program the merge for an AndQuery, by gathering the postings of the composed QueryComponents and
        #  intersecting the resulting postings.
        temp = []
        for i in self.components:
            temp.append(i.get_postings(index, processor))

        # for _ in range(temp.count(None)):
        #     temp.remove(None)

        if len(temp) > 0:
            p1 = temp[0]
            postingTrack = 1
            while postingTrack < len(temp):
                p2 = temp[postingTrack]
                pointer1 = 0
                pointer2 = 0
                mergeList = []
                if (p1 is not None) and (p2 is not None):
                    while pointer1 < len(p1) and pointer2 < len(p2):
                        if self.components[postingTrack].is_positive():
                            if p1[pointer1].get_doc_id() < p2[pointer2].get_doc_id():
                                pointer1 += 1

                            elif p2[pointer2].get_doc_id() < p1[pointer1].get_doc_id():
                                pointer2 += 1

                            else:
                                mergeList.append(Posting(p1[pointer1].get_doc_id()))
                                pointer1 += 1
                                pointer2 += 1
                        else:
                            if p1[pointer1].get_doc_id() < p2[pointer2].get_doc_id():
                                mergeList.append(Posting(p1[pointer1].get_doc_id()))
                                pointer1 += 1

                            elif p2[pointer2].get_doc_id() < p1[pointer1].get_doc_id():
                                # mergeList.append(Posting(p2[pointer2].get_doc_id()))
                                pointer2 += 1

                            else:
                                pointer1 += 1
                                pointer2 += 1

                    while pointer1 < len(p1):
                        mergeList.append(Posting(p1[pointer1].get_doc_id()))
                        pointer1 += 1

                    # while pointer2 < len(p2):
                    #     mergeList.append(Posting(p2[pointer2].get_doc_id()))
                    #     pointer2 += 1

                    p1 = deepcopy(mergeList)
                postingTrack += 1

            result = deepcopy(p1)
            return result
        return []

    def __str__(self):
        return " AND ".join(map(str, self.components))