from typing import Dict, Any
from datetime import datetime
from snowline.core.tool_registry import ToolRegistry
from snowline.domains.checks import SafetyValidator, RiskAssessor, GuidanceGenerator
from snowline.core.state_manager import StateManager
from snowline.tools.smart_replace import SmartReplace

class SnowlineCompanion:
    """
    The main orchestrator for the Snowline Agentic OS.
    Acts as the entry point for agents to interact with tools.
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.registry = ToolRegistry()
        
        db_path = self.config.get("state_db", "./.snowline/state.db")
        self.state = StateManager(db_path=db_path)
        
        # Register core tools
        self.registry.register(SmartReplace(workspace_dir="."))
        
        self.validator = SafetyValidator()
        self.assessor = RiskAssessor()
        self.guidance_gen = GuidanceGenerator()
        
    def handle_request(self, agent_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an agent's request to execute a tool, providing guidance
        and dry-run previews without actually committing destructive changes.
        """
        tool_name = agent_request.get("tool")
        
        # 1. Validation & Risk Assessment
        validation = self.validator.validate(agent_request)
        risk = self.assessor.score(agent_request)
        
        # 2. Generate Guidance
        guidance = self.guidance_gen.generate(validation, risk)
        
        # 3. Simulate Dry Run if tool exists
        tool = self.registry.get_tool(tool_name)
        preview_data = {}
        if tool:
            try:
                # Ensure dry_run=True when handling request for preview
                safe_params = dict(agent_request.get("params", {}))
                safe_params["dry_run"] = True
                preview_data = tool.dry_run(safe_params)
            except Exception as e:
                preview_data = {"error": str(e)}
        else:
            if tool_name:
                preview_data = {"error": f"Tool '{tool_name}' not found."}
        
        # 4. Construct Structured Response
        return {
            "snowline_response": {
                "status": "success" if validation.safe else "blocked",
                "tool": tool_name,
                "timestamp": datetime.now().isoformat(),
                "verdict": {
                    "safe": validation.safe,
                    "confidence": 90 if tool else 0,
                    "reasoning": "Validasi keamanan dilewati." if validation.safe else "Ditolak oleh sistem."
                },
                "guidance": guidance.to_dict(),
                "metadata": {
                    "risks": validation.risks,
                    "risk_score": risk.score,
                    "risk_level": risk.level
                },
                "dry_run": {
                    "enabled": True,
                    "preview": preview_data,
                    "reversal_plan": "Pastikan ada mekanisme backup sebelum proceed."
                }
            }
        }
        
    def execute(self, agent_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actually execute the requested action. Assumes the agent has
        received 'proceed' guidance and chosen to proceed.
        """
        tool_name = agent_request.get("tool")
        params = agent_request.get("params", {})
        
        tool = self.registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found in registry.")
            
        # Optional re-validation
        validation = self.validator.validate(agent_request)
        if not validation.safe:
            raise PermissionError("Cannot execute unsafe action.")
            
        import uuid
        exec_id = f"exec_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.state.start_execution(exec_id, tool_name)
        
        try:
            result = tool.execute(params)
            self.state.save_artifact("execution_result", result)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
