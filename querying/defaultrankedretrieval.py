import math
from querying import RankedRetrieval


class DefaultRetrieval(RankedRetrieval):

    def get_wdt(self, tftd):
        return 1 + math.log(tftd)

    def get_Ld(self, docid):
        # TODO: Implement this
        pass

    def get_wqt(self, dft, N):
        return math.log(1 + (N/dft))
