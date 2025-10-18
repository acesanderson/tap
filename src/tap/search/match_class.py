from pydantic import BaseModel
from typing import override


class Match(BaseModel):
    title: str
    score: float
    rank: int


class Matches(BaseModel):
    query: str
    results: list[Match]

    @override
    def __str__(self) -> str:
        output = f"# Query: {self.query}\n"
        for match in self.results:
            output += f"[{match.rank}] {match.title} (Score: {match.score})\n"
        return output
