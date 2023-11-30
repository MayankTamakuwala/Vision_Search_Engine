import math
from querying import RankedRetrieval
from database import get_client


class ProbabilityRetrieval(RankedRetrieval):
    def __init__(self, path):
        self.client = get_client()
        self.collection = self.client["Weights"]["1" + path[1:] if path[0] == "." else path]

    def get_wdt(self, tftd, docid):
        doclength_d = self.collection.find_one({"doc_id": docid})["token_count"]
        doclength_A = self.collection.find_one({"type": "Length A"})["docLengthA"]
        num = (2.2 * tftd)
        den = ((1.2 * (0.25 + (0.75 * (doclength_d/doclength_A)))) + tftd)
        return num/den

    def get_Ld(self, docid):
        return 1

    def get_wqt(self, dft, N):
        return max(0.1, math.log((N-dft+0.5)/(dft + 0.5)))
