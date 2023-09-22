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
        else:
            subTokens.append(token)

        for i in range(len(subTokens)):

            start = 0
            end = len(subTokens[i])

            while (not subTokens[i][start].isalnum()) and start < end:
                start += 1

            while (not subTokens[i][end - 1].isalnum()) and end > start:
                end -= 1

            subTokens[i] = subTokens[i][start:end]

        for i in range(len(subTokens)):
            temp = subTokens[i].replace("\'", "")
            subTokens[i] = temp.replace("\"", "").lower()

        return list(set(subTokens))

    def normalize_type(self, type: list[str]) -> list[str]:
        stemmer = Porter2Stemmer()
        for i in range(len(type)):
            type[i] = stemmer.stem(type[i])
        return type