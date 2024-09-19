from pydantic import BaseModel


class Complaints(BaseModel):

    complaints: list[str]
    percentages: list[int]


class Suggestions(BaseModel):

    suggestions: list[str]
    percentages: list[int]
