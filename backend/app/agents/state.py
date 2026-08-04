from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    session_id: str
    user_id: int
    user_input: str
    current_intent: str
    conversation_history: List[Dict[str, str]]
    agent_scratchpad: List[str]
    retrieved_documents: List[str]
    final_response: str
    offline_mode: bool
    errors: List[str]
