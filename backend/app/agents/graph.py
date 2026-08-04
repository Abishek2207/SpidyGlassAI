from langgraph.graph import StateGraph, END
from app.agents.state import AgentState

from app.agents.nodes.coordinator_node import coordinator_node
from app.agents.nodes.vision_node import vision_node
from app.agents.nodes.speech_node import speech_node
from app.agents.nodes.translation_node import translation_node
from app.agents.nodes.conversation_node import conversation_node
from app.agents.nodes.medical_node import medical_node
from app.agents.nodes.accessibility_node import accessibility_node
from app.agents.nodes.system_node import system_node
from app.agents.nodes.scheduler_node import scheduler_node
from app.agents.nodes.knowledge_node import knowledge_node

def route_from_coordinator(state: AgentState):
    intent = state.get("current_intent", "conversation")
    mapping = {
        "vision": "vision",
        "speech": "speech",
        "translation": "translation",
        "conversation": "conversation",
        "medical": "medical",
        "accessibility": "accessibility",
        "system": "system",
        "scheduler": "scheduler",
        "knowledge": "knowledge"
    }
    return mapping.get(intent, "conversation")

graph = StateGraph(AgentState)

graph.add_node("coordinator", coordinator_node)
graph.add_node("vision", vision_node)
graph.add_node("speech", speech_node)
graph.add_node("translation", translation_node)
graph.add_node("conversation", conversation_node)
graph.add_node("medical", medical_node)
graph.add_node("accessibility", accessibility_node)
graph.add_node("system", system_node)
graph.add_node("scheduler", scheduler_node)
graph.add_node("knowledge", knowledge_node)

graph.set_entry_point("coordinator")

graph.add_conditional_edges(
    "coordinator",
    route_from_coordinator
)

# All specialized nodes just end for now. We can add more complex routing later.
for node in ["vision", "speech", "translation", "conversation", "medical", "accessibility", "system", "scheduler", "knowledge"]:
    graph.add_edge(node, END)

app_graph = graph.compile()
