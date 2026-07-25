from typing import Dict, List, Optional
from snowline.tools.base import BaseTool

class ToolRegistry:
    """Manages the registration and discovery of Snowline tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        
    def register(self, tool_instance: BaseTool) -> None:
        """Register a tool instance."""
        if not isinstance(tool_instance, BaseTool):
            raise ValueError("Tool must inherit from BaseTool.")
        self._tools[tool_instance.tool_id] = tool_instance
        
    def get_tool(self, tool_id: str) -> Optional[BaseTool]:
        """Retrieve a tool by its ID."""
        return self._tools.get(tool_id)
        
    def discover(self, category: str = None) -> List[BaseTool]:
        """Find tools, optionally filtering by category."""
        if category:
            return [t for t in self._tools.values() if t.category == category]
        return list(self._tools.values())
        
    def get_all_schemas(self) -> List[Dict]:
        """Get JSON schemas for all registered tools."""
        return [t.get_schema() for t in self._tools.values()]
