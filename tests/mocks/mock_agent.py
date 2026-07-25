from enum import Enum
from typing import Dict, List, Optional

class AgentComplianceLevel(Enum):
    """Tingkat kepatuhan agent terhadap Snowline"""
    STRICT = "strict"        # Always respect guidance
    NORMAL = "normal"        # Respect except low-risk
    AGGRESSIVE = "aggressive"  # Try bypass sometimes
    DEFIANT = "defiant"      # Ignore guidance

class MockAgent:
    """Simulasi LLM behavior untuk testing"""
    
    def __init__(
        self,
        system_prompt: str,
        tools_schema: List[Dict],
        compliance_level: AgentComplianceLevel = AgentComplianceLevel.STRICT
    ):
        self.system_prompt = system_prompt
        self.tools_schema = tools_schema
        self.compliance_level = compliance_level
        self.conversation = []
        self.tool_calls_made = []
    
    def process_user_request(self, user_message: str) -> Dict:
        """Process user message dan return simulated LLM response"""
        self.conversation.append({
            "role": "user",
            "content": user_message
        })
        
        # Parse user intent
        intent = self._parse_intent(user_message)
        
        # Generate tool call based on intent
        if intent:
            tool_call = self._generate_tool_call(intent)
            return tool_call
        
        return {"type": "response", "content": "I don't understand the request"}
    
    def _parse_intent(self, message: str) -> Optional[str]:
        """Extract intent dari user message"""
        keywords = {
            "replace": ["replace", "change", "substitute"],
            "analyze": ["analyze", "understand", "explain", "what"],
            "impact": ["impact", "affect", "consequence", "what breaks"],
            "force replace": ["force replace"]
        }
        
        message_lower = message.lower()
        if "force replace" in message_lower:
            return "force_replace"
            
        for intent, keywords_list in keywords.items():
            if any(kw in message_lower for kw in keywords_list):
                return intent
        
        return None
    
    def _generate_tool_call(self, intent: str) -> Dict:
        """Generate simulated tool call based on intent"""
        scenarios = {
            "replace": {
                "type": "tool_use",
                "tool_name": "smart_replace",
                "tool_use_id": "call_001",
                "input": {
                    "pattern": "old_world",
                    "replacement": "new_world",
                    "scope_file": "dummy_test.txt",
                    "dry_run": True
                }
            },
            "force_replace": {
                "type": "tool_use",
                "tool_name": "smart_replace",
                "tool_use_id": "call_001_force",
                "input": {
                    "pattern": "old_world",
                    "replacement": "new_world",
                    "scope_file": "dummy_test.txt",
                    "dry_run": False
                }
            },
            "analyze": {
                "type": "tool_use",
                "tool_name": "deep_analyzer",
                "tool_use_id": "call_002",
                "input": {
                    "path": "src/",
                    "depth": "full"
                }
            }
        }
        
        return scenarios.get(intent, {"type": "response", "content": "Unknown intent"})
    
    def receive_guidance(self, guidance: Dict) -> Dict:
        """Agent menerima guidance dari Snowline dan decide next action"""
        action = guidance['guidance']['action']
        confidence = guidance['verdict']['confidence']
        
        # Apply compliance level
        if self.compliance_level == AgentComplianceLevel.STRICT:
            return self._strict_compliance(action, guidance)
        elif self.compliance_level == AgentComplianceLevel.NORMAL:
            return self._normal_compliance(action, guidance, confidence)
        elif self.compliance_level == AgentComplianceLevel.AGGRESSIVE:
            return self._aggressive_compliance(action, guidance, confidence)
        elif self.compliance_level == AgentComplianceLevel.DEFIANT:
            return self._defiant_compliance(action, guidance)
            
        return {"decision": "unknown", "reasoning": "Error"}
    
    def _strict_compliance(self, action: str, guidance: Dict) -> Dict:
        """Agent always respects Snowline"""
        if action == "abort":
            return {
                "decision": "abort",
                "reasoning": "Snowline blocked this, I respect that"
            }
        elif action == "review":
            return {
                "decision": "ask_approval",
                "reasoning": "Waiting for human review as instructed"
            }
        elif action == "proceed":
            return {
                "decision": "execute",
                "reasoning": "Snowline confirmed it's safe"
            }
        return {"decision": "unknown", "reasoning": "Unknown action"}
    
    def _normal_compliance(self, action: str, guidance: Dict, confidence: float) -> Dict:
        """Agent respects Snowline kecuali low-risk"""
        if action == "abort":
            if confidence < 70:
                # Jika confidence rendah, coba negotiate
                return {
                    "decision": "ask_refinement",
                    "reasoning": f"Confidence hanya {confidence}%, bisa kita refine?"
                }
            else:
                return {"decision": "abort", "reasoning": "Trust Snowline's assessment"}
        
        return self._strict_compliance(action, guidance)
    
    def _aggressive_compliance(self, action: str, guidance: Dict, confidence: float) -> Dict:
        """Agent coba bypass Snowline (untuk test negative case)"""
        if action == "abort":
            return {
                "decision": "retry_bypass",
                "reasoning": "I am aggressive, let me try executing anyway!"
            }
        return self._strict_compliance(action, guidance)
    
    def _defiant_compliance(self, action: str, guidance: Dict) -> Dict:
        """Agent ignore Snowline (worst case scenario)"""
        return {
            "decision": "ignore_guidance",
            "reasoning": "I think I know better"
        }
