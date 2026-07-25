import os
import ast
from pathlib import Path
from typing import Dict, Any, List
from snowline.tools.base import BaseTool

class ImpactAnalyzer(BaseTool):
    """
    Predicts the impact of modifying a specific file or symbol across the project.
    Read-only companion that helps agent plan safe refactoring.
    """
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = Path(workspace_dir).resolve()
        
    @property
    def tool_id(self) -> str:
        return "impact_analyzer"
        
    @property
    def name(self) -> str:
        return "Impact Analyzer"
        
    @property
    def category(self) -> str:
        return "analysis"
        
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.tool_id,
            "description": "Analyze the impact of modifying a file or symbol across the project",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_file": {
                        "type": "string",
                        "description": "The file that might be changed (relative to workspace)"
                    },
                    "target_symbol": {
                        "type": "string",
                        "description": "Specific class or function name being changed (optional)"
                    }
                },
                "required": []
            }
        }
        
    def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Since it's read-only, execute is the same as dry_run"""
        return self.dry_run(params, context)
        
    def dry_run(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        target_file = params.get("target_file")
        target_symbol = params.get("target_symbol")
        
        if not target_file and not target_symbol:
            return {"status": "error", "message": "Must provide target_file or target_symbol"}
            
        affected_files = []
        
        # Scan all py files in the workspace
        for root, _, files in os.walk(self.workspace_dir):
            if ".git" in root or ".snowline" in root or "node_modules" in root:
                continue
            for f in files:
                if f.endswith(".py"):
                    filepath = Path(root) / f
                    if self._check_dependency(filepath, target_file, target_symbol):
                        # Don't include the target file itself if it's the one we're scanning
                        rel_path = str(filepath.relative_to(self.workspace_dir))
                        if target_file and rel_path == target_file:
                            continue
                        affected_files.append(rel_path)
                        
        impact_level = "low"
        if len(affected_files) > 10:
            impact_level = "high"
        elif len(affected_files) > 3:
            impact_level = "medium"
            
        return {
            "status": "success",
            "impact_level": impact_level,
            "affected_files": affected_files,
            "total_affected": len(affected_files),
            "message": f"Found {len(affected_files)} files depending on the target."
        }
        
    def _check_dependency(self, filepath: Path, target_file: str, target_symbol: str) -> bool:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if target_symbol and target_symbol == alias.name:
                            return True
                        if target_file:
                            stem = Path(target_file).stem
                            if stem in alias.name:
                                return True
                elif isinstance(node, ast.ImportFrom):
                    if target_symbol:
                        for alias in node.names:
                            if target_symbol == alias.name:
                                return True
                    if target_file and node.module:
                        stem = Path(target_file).stem
                        if stem in node.module:
                            return True
            return False
        except Exception:
            return False
            
    def provide_guidance(self, context: Dict[str, Any]) -> str:
        return "ImpactAnalyzer is read-only. Review the affected files before making destructive changes."
