import math
from querying import RankedRetrieval


class ProbabilityRetrieval(RankedRetrieval):

    def get_wdt(self, tftd):
        # TODO: Implement This
        pass

    def get_Ld(self, docid):
        return 1

    def get_wqt(self, dft, N):
        return max(0.1, math.log((N-dft+0.5)/(dft + 0.5)))