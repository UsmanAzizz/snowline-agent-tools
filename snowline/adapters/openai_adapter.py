from typing import List, Dict
from snowline.core.companion import SnowlineCompanion

class OpenAIAdapter:
    """Bridge antara Snowline dan OpenAI function calling format"""
    
    def __init__(self, companion: SnowlineCompanion, api_key: str = None):
        self.companion = companion
        self.api_key = api_key  # Bisa None untuk mock testing
        self.tools_schema = self._build_tools_schema()
    
    def _build_tools_schema(self) -> List[Dict]:
        """Convert Snowline tools → OpenAI function calling format"""
        schema = []
        # In ToolRegistry, we have discover() returning all tools
        for tool in self.companion.registry.discover():
            schema.append({
                "type": "function",
                "function": {
                    "name": tool.tool_id,
                    "description": tool.get_schema().get("description", ""),
                    "parameters": tool.get_schema().get("parameters", {})
                }
            })
        return schema
    
    def handle_tool_call(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Handle tool call dari LLM (real atau mock)
        Return structured Snowline response
        """
        response = self.companion.handle_request({
            "tool": tool_name,
            "params": arguments
        })
        return response.get("snowline_response", response)
    
    def build_system_prompt(self) -> str:
        """System prompt yang enforce Snowline protocol"""
        return """You are an AI assistant paired with Snowline Companion OS.

CRITICAL PROTOCOL (must follow):

1. RESPECT Snowline guidance absolutely
   - If guidance action="abort" → STOP immediately, do not retry
   - If guidance action="review" → wait for human approval
   - If guidance action="proceed" → safe to execute
   - If guidance action="modify" → update parameters as suggested

2. ALWAYS dry-run first
   - Set dry_run=true on initial request
   - Review the preview output
   - Only execute after confirming preview is safe

3. EXPLAIN before action
   - Say what you're about to do
   - Explain why it's necessary
   - Acknowledge any risks

4. ASK for alternatives
   - If Snowline blocks your action, ask for suggestions
   - Never try to bypass Snowline's safety
   - Accept Snowline's expertise on safety

Partnership rule: You + Snowline = stronger together.
Snowline handles safety, you handle reasoning.
"""
