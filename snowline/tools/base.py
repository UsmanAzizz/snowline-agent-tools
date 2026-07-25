from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseTool(ABC):
    """Base class for all Snowline tools."""
    
    @property
    @abstractmethod
    def tool_id(self) -> str:
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def category(self) -> str:
        pass
        
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Return the JSON schema representation of the tool."""
        pass
        
    @abstractmethod
    def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Actually run the tool."""
        pass
        
    @abstractmethod
    def dry_run(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Preview the execution safely without mutating state."""
        pass
        
    def provide_guidance(self, context: Dict[str, Any]) -> str:
        """Provide companion wisdom for the agent about this tool."""
        return "Always verify parameters before execution."
