from abc import ABC


class RankedRetrieval(ABC):

    def get_wdt(self, tftd, docid):
        pass

    def get_Ld(self, docid):
        pass

    def get_wqt(self, dft, N):
        pass
