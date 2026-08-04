import os
nodes = ['vision', 'speech', 'translation', 'conversation', 'medical', 'accessibility', 'system', 'scheduler', 'knowledge', 'coordinator']
for node in nodes:
    path = f'app/agents/nodes/{node}_node.py'
    with open(path, 'w') as f:
        f.write(f'''from app.agents.state import AgentState\nfrom typing import Dict, Any\n\nasync def {node}_node(state: AgentState) -> Dict[str, Any]:\n    return {{"agent_scratchpad": state.get("agent_scratchpad", []) + ["{node} executed"]}}\n''')
print('done')
