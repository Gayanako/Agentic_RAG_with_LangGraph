# from typing import Annotated, Dict, List, TypedDict
# from langchain_core.messages import BaseMessage

# class GraphState(TypedDict):
#     """Represents the state of our graph."""
#     original_question:str
#     question: str
#     generation: Annotated[str, ""]
#     web_search: bool
#     documents: List[BaseMessage]
#     unique_sources: set
#     web_sources: list
#     retry_count: int
#     messages: Annotated[List[BaseMessage], "List of conversation messages"]
#     # New fields for multi-LLM
#     gemini_answer: Annotated[str, ""]
#     perplexity_answer: Annotated[str, ""]
#     validation_reasoning: Annotated[str, ""]
#     chosen_model: Annotated[str, ""]
#     validation_result: dict 


######################################UPDATED CODE FOR METRIC EVALUATION CONTEXT BASED##################################################
# src/workflow/state.py
from typing import Annotated, Dict, List, TypedDict, Any, Union
from langchain_core.messages import BaseMessage
import numpy as np

class GraphState(TypedDict):
    """Represents the state of our graph."""
    original_question: str
    question: str
    generation: Annotated[str, ""]
    web_search: bool
    documents: List[Any]  # Changed from BaseMessage to Any for flexibility
    unique_sources: set
    web_sources: list
    retry_count: int
    messages: Annotated[List[BaseMessage], "List of conversation messages"]
    # New fields for multi-LLM
    gemini_answer: Annotated[str, ""]
    perplexity_answer: Annotated[str, ""]
    validation_reasoning: Annotated[str, ""]
    chosen_model: Annotated[str, ""]
    validation_result: Dict[str, Any]  # Make sure this is JSON serializable

def convert_numpy_types(obj: Any) -> Any:
    """Convert numpy types to Python native types for serialization."""
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    else:
        return obj

