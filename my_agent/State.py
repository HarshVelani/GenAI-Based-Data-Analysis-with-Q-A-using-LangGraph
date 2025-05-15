from typing import List, Any, Annotated, Dict, Optional
from typing_extensions import TypedDict
import operator

class InputState(TypedDict):
    question: str
    path: str
    parsed_question: Dict[str, Any]
    unique_nouns: List[str]
    results: List[Any]
    visualization: Annotated[str, operator.add]
    visualization_reason: Annotated[str, operator.add]

class OutputState(TypedDict):
    parsed_question: Dict[str, Any]
    unique_nouns: List[str]
    results: List[Any]
    answer: Annotated[str, operator.add]
    error: str
    visualization: Annotated[str, operator.add]
    visualization_reason: Annotated[str, operator.add]
    visualization_code: Dict[str, Any]
    