import os
import re
import uuid
import shutil
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from snowline.tools.base import BaseTool

class SmartReplace(BaseTool):
    """
    A tool to safely replace text or regex patterns across files.
    Includes built-in backup and dry-run capabilities.
    """
    
    def __init__(self, workspace_dir: str = "."):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.backup_dir = self.workspace_dir / ".snowline" / "backups"
        
    @property
    def tool_id(self) -> str:
        return "smart_replace"
        
    @property
    def name(self) -> str:
        return "Smart Replace"
        
    @property
    def category(self) -> str:
        return "execution"
        
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.tool_id,
            "description": "Safe code replacement with backup & preview",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex or literal pattern to find"
                    },
                    "replacement": {
                        "type": "string",
                        "description": "Replacement string"
                    },
                    "scope_file": {
                        "type": "string",
                        "description": "Specific file to modify (relative to workspace). Optional if targeting directory."
                    },
                    "scope_dir": {
                        "type": "string",
                        "description": "Directory to scan (relative to workspace)."
                    },
                    "is_regex": {
                        "type": "boolean",
                        "description": "Set to true if pattern is a regex",
                        "default": False
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Preview mode without modifying files",
                        "default": True
                    }
                },
                "required": ["pattern", "replacement"]
            }
        }
        
    def _find_files(self, scope_file: str, scope_dir: str) -> List[Path]:
        files = []
        if scope_file:
            path = (self.workspace_dir / scope_file).resolve()
            if path.exists() and path.is_file():
                files.append(path)
        elif scope_dir:
            dir_path = (self.workspace_dir / scope_dir).resolve()
            if dir_path.exists() and dir_path.is_dir():
                for root, _, filenames in os.walk(dir_path):
                    if ".git" in root or ".snowline" in root or "node_modules" in root:
                        continue
                    for f in filenames:
                        files.append(Path(root) / f)
        else:
            # Fallback to current dir
            for root, _, filenames in os.walk(self.workspace_dir):
                if ".git" in root or ".snowline" in root or "node_modules" in root:
                    continue
                for f in filenames:
                    files.append(Path(root) / f)
        return files
        
    def _perform_replacement(self, file_path: Path, pattern: str, replacement: str, is_regex: bool, execute: bool) -> List[Dict]:
        matches = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            if is_regex:
                # Find matches for preview
                for i, line in enumerate(content.splitlines()):
                    if re.search(pattern, line):
                        matches.append({"line": i + 1, "original": line.strip()})
                if execute and matches:
                    new_content = re.sub(pattern, replacement, content)
            else:
                for i, line in enumerate(content.splitlines()):
                    if pattern in line:
                        matches.append({"line": i + 1, "original": line.strip()})
                if execute and matches:
                    new_content = content.replace(pattern, replacement)
                    
            if execute and matches:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                    
        except Exception as e:
            pass # Skip binary files or decoding errors
            
        return matches

    def dry_run(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        pattern = params.get("pattern")
        replacement = params.get("replacement")
        scope_file = params.get("scope_file")
        scope_dir = params.get("scope_dir")
        is_regex = params.get("is_regex", False)
        
        target_files = self._find_files(scope_file, scope_dir)
        preview_data = []
        total_matches = 0
        
        for file_path in target_files:
            matches = self._perform_replacement(file_path, pattern, replacement, is_regex, execute=False)
            if matches:
                preview_data.append({
                    "file": str(file_path.relative_to(self.workspace_dir)),
                    "matches": len(matches),
                    "details": matches[:5] # show max 5 matches per file in preview
                })
                total_matches += len(matches)
                
        return {
            "total_matches": total_matches,
            "affected_files": len(preview_data),
            "preview": preview_data,
            "message": f"Preview mode: {total_matches} occurrences found in {len(preview_data)} files."
        }

    def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Enforce dry-run explicitly checking
        is_dry_run = params.get("dry_run", False)
        if is_dry_run:
            return self.dry_run(params, context)
            
        pattern = params.get("pattern")
        replacement = params.get("replacement")
        scope_file = params.get("scope_file")
        scope_dir = params.get("scope_dir")
        is_regex = params.get("is_regex", False)
        
        target_files = self._find_files(scope_file, scope_dir)
        affected_files = []
        
        # 1. Identify files that will change
        for file_path in target_files:
            matches = self._perform_replacement(file_path, pattern, replacement, is_regex, execute=False)
            if matches:
                affected_files.append(file_path)
                
        if not affected_files:
            return {"status": "success", "message": "No matches found.", "affected_files": 0}
            
        # 2. Create Backup
        backup_id = str(uuid.uuid4())
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)
        
        backup_metadata = []
        for file_path in affected_files:
            rel_path = file_path.relative_to(self.workspace_dir)
            dest = backup_path / "files" / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest)
            backup_metadata.append(str(rel_path))
            
        with open(backup_path / "metadata.json", "w", encoding="utf-8") as f:
            json.dump({"backup_id": backup_id, "files": backup_metadata}, f)
            
        # 3. Perform Replacement
        total_matches = 0
        for file_path in affected_files:
            matches = self._perform_replacement(file_path, pattern, replacement, is_regex, execute=True)
            total_matches += len(matches)
            
        return {
            "status": "success",
            "matches_replaced": total_matches,
            "affected_files": len(affected_files),
            "backup_id": backup_id,
            "reversal_command": f"Rollback available via backup_id: {backup_id}"
        }
        
    def rollback(self, backup_id: str) -> Dict[str, Any]:
        """Restore files from a specific backup ID."""
        backup_path = self.backup_dir / backup_id
        meta_file = backup_path / "metadata.json"
        
        if not backup_path.exists() or not meta_file.exists():
            return {"status": "error", "message": "Backup not found."}
            
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
            
        restored = 0
        for rel_path_str in meta.get("files", []):
            backup_file = backup_path / "files" / rel_path_str
            target_file = self.workspace_dir / rel_path_str
            if backup_file.exists():
                shutil.copy2(backup_file, target_file)
                restored += 1
                
        return {
            "status": "success",
            "message": f"Successfully restored {restored} files from backup {backup_id}."
        }

    def provide_guidance(self, context: Dict[str, Any]) -> str:
        return (
            "SmartReplace modifies source code. Always use `dry_run: true` first to preview the changes. "
            "If the changes look correct, execute with `dry_run: false`. If a mistake is made, you can use the returned "
            "`backup_id` to request a manual rollback."
        )
