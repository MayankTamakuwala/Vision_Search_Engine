import math
from querying import RankedRetrieval
from database import get_client


class DefaultRetrieval(RankedRetrieval):

    def __init__(self, path):
        self.client = get_client()
        self.collection = self.client["Weights"]["1" + path[1:] if path[0] == "." else path]

    def get_wdt(self, tftd, docid):
        return 1 + math.log(tftd)

    def get_Ld(self, docid):
        return self.collection.find_one({"doc_id": docid})["L_d"]

    def get_wqt(self, dft, N):
        return math.log(1 + (N/dft))
