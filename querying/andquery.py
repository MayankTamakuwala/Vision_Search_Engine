from .querycomponent import QueryComponent
from indexing import Index, Posting
from querying import querycomponent 

class AndQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        # please don't rename the "components" field.
        self.components = components

    def get_postings(self, index : Index, processor) -> list[Posting]:
        result = []
        # temp = []
        # for i in self.components:
        #     temp.append(i.get_postings(index))
        # TODO: program the merge for an AndQuery, by gathering the postings of the composed QueryComponents and
        #  intersecting the resulting postings.
        return result

    def __str__(self):
        return " AND ".join(map(str, self.components))