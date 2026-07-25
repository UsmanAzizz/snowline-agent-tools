import ast
import os
from typing import Dict, Any, List
from snowline.tools.base import BaseTool

class DeepAnalyzer(BaseTool):
    """
    Analyze code structure, dependencies, complexity.
    Read-only companion that helps agent understand code.
    """
    
    @property
    def tool_id(self) -> str:
        return "deep_analyzer"
        
    @property
    def name(self) -> str:
        return "Deep Analyzer"
        
    @property
    def category(self) -> str:
        return "analysis"
        
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.tool_id,
            "description": "Analyze code structure, flow, and dependencies",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File or directory path to analyze"
                    },
                    "depth": {
                        "type": "string",
                        "enum": ["shallow", "medium", "deep"],
                        "description": "Analysis depth"
                    }
                },
                "required": ["path"]
            }
        }
    
    def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze code structure (Same as dry-run because it's read-only)"""
        return self.dry_run(params, context)
    
    def dry_run(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Return analysis without modifying anything"""
        path = params.get("path")
        depth = params.get("depth", "medium")
        
        if not path or not os.path.exists(path):
            return {"status": "error", "message": f"Path not found: {path}"}
            
        analysis = {
            "path": path,
            "type": "file" if os.path.isfile(path) else "directory",
            "structure": self._analyze_structure(path),
            "dependencies": self._extract_dependencies(path),
            "complexity": self._measure_complexity(path),
            "insights": self._generate_insights(path, depth)
        }
        
        return {
            "status": "success",
            "analysis": analysis
        }
    
    def _analyze_structure(self, path: str) -> Dict[str, Any]:
        """Analyze code structure"""
        if os.path.isfile(path) and path.endswith(".py"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                
                functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                
                return {
                    "functions": functions,
                    "classes": classes,
                    "total_functions": len(functions),
                    "total_classes": len(classes)
                }
            except Exception as e:
                return {"error": f"Could not parse file: {str(e)}"}
        
        return {"message": "Non-Python file, skipping AST analysis"}
    
    def _extract_dependencies(self, path: str) -> List[str]:
        """Extract import dependencies"""
        deps = []
        if os.path.isfile(path) and path.endswith(".py"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            deps.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        deps.append(node.module or ".")
            except Exception:
                pass
        return list(set(deps))
    
    def _measure_complexity(self, path: str) -> Dict[str, Any]:
        """Measure code complexity"""
        if not os.path.isfile(path) or not path.endswith(".py"):
            return {"message": "Complexity analysis for Python files only"}
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            return {
                "lines_of_code": len(lines),
                "empty_lines": sum(1 for line in lines if not line.strip()),
                "comment_lines": sum(1 for line in lines if line.strip().startswith("#")),
                "cyclomatic_estimate": self._estimate_cyclomatic(lines)
            }
        except Exception as e:
            return {"error": f"Could not measure complexity: {str(e)}"}
    
    def _estimate_cyclomatic(self, lines: List[str]) -> int:
        """Simple cyclomatic complexity estimate"""
        count = 1
        for line in lines:
            if any(keyword in line for keyword in ['if ', 'for ', 'while ', 'except ', 'and ', 'or ']):
                count += 1
        return count
    
    def _generate_insights(self, path: str, depth: str) -> List[str]:
        """Generate analysis insights"""
        insights = []
        if os.path.isfile(path):
            size_kb = os.path.getsize(path) / 1024
            if size_kb > 50:
                insights.append(f"Large file ({size_kb:.1f}KB) - consider breaking into modules")
        return insights

    def provide_guidance(self, context: Dict[str, Any]) -> str:
        return (
            "DeepAnalyzer is read-only and safe. Use the insights provided to "
            "better understand the code structure before planning any refactoring."
        )
