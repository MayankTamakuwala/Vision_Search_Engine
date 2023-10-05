from .tokenprocessor import TokenProcessor
from porter2stemmer import Porter2Stemmer

class NewTokenProcessor(TokenProcessor):
    """A NewTokenProcessor creates terms from tokens by removing all non-alphanumeric characters
    from the token, and converting it to all lowercase."""

    def process_token(self, token: str) -> list[str]:
        subTokens = []

        if token.count("-") > 0:
            subTokens = token.split("-")
            subTokens.append("".join(subTokens))
            for _ in range(subTokens.count("")):
                subTokens.remove("")

        else:
            subTokens.append(token)

        for i in range(len(subTokens)):
            temp = subTokens[i].replace("\'", "")
            subTokens[i] = temp.replace("\"", "").lower()

        for i in range(len(subTokens)):

            start = 0
            end = len(subTokens[i])

            while start < end and (not subTokens[i][start].isalnum()):
                start += 1

            while end > start and (not subTokens[i][end - 1].isalnum()):
                end -= 1

            subTokens[i] = subTokens[i][start:end]

        return list(set(subTokens))

    def normalize_type(self, type: list[str]) -> list[str]:
        stemmer = Porter2Stemmer()
        for i in range(len(type)):
            type[i] = stemmer.stem(type[i])
        return type