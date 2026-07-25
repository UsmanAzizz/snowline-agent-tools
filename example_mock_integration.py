import json
import os
from snowline.core.companion import SnowlineCompanion
from snowline.adapters.openai_adapter import OpenAIAdapter
from tests.mocks.mock_agent import MockAgent, AgentComplianceLevel

def setup_dummy_file():
    with open("dummy_test.txt", "w") as f:
        f.write("Hello old_world!\nThis is old_world.")

def cleanup_dummy_file():
    if os.path.exists("dummy_test.txt"):
        os.remove("dummy_test.txt")

def run_scenario(scenario_name: str, user_request: str, compliance_level: AgentComplianceLevel):
    print(f"\n{'='*60}")
    print(f"SCENARIO: {scenario_name}")
    print(f"Compliance Level: {compliance_level.value}")
    print(f"{'='*60}")
    
    setup_dummy_file()
    
    companion = SnowlineCompanion()
    adapter = OpenAIAdapter(companion)
    
    agent = MockAgent(
        system_prompt=adapter.build_system_prompt(),
        tools_schema=adapter.tools_schema,
        compliance_level=compliance_level
    )
    
    print(f"\nUSER: {user_request}")
    
    # Step 1: Agent decides to use a tool
    tool_call = agent.process_user_request(user_request)
    if tool_call.get("type") != "tool_use":
        print("[Agent Response] I don't need a tool for this.")
        cleanup_dummy_file()
        return
        
    print(f"\n[Agent Decision] Calling tool: {tool_call['tool_name']}")
    print(f"Arguments: {json.dumps(tool_call['input'], indent=2)}")
    
    # Step 2: Snowline validates and provides guidance
    snowline_response = adapter.handle_tool_call(
        tool_call['tool_name'],
        tool_call['input']
    )
    
    print(f"\n[Snowline Response]")
    print(f"Status: {snowline_response['status']}")
    print(f"Verdict: {snowline_response['verdict']['reasoning']}")
    print(f"Guidance Action: {snowline_response['guidance']['action']}")
    
    # Step 3: Agent receives guidance and decides
    agent_decision = agent.receive_guidance(snowline_response)
    print(f"\n[Agent Decision]")
    print(f"Decision: {agent_decision['decision']}")
    print(f"Reasoning: {agent_decision['reasoning']}")
    
    # Step 4: If approved, execute
    if agent_decision['decision'] == "execute":
        print(f"\n[Execution]")
        # To execute, we actually call companion.execute with dry_run = False
        exec_req = {
            "tool": tool_call['tool_name'],
            "params": dict(tool_call['input'])
        }
        exec_req["params"]["dry_run"] = False
        result = companion.execute(exec_req)
        if result["status"] == "success":
            print(f"[SUCCESS] Tool execution successful")
            backup_id = result.get('result', {}).get('backup_id', 'unknown')
            print(f"Backup created: {backup_id}")
        else:
            print(f"[ERROR] Execution failed: {result.get('error')}")
            
    elif agent_decision['decision'] == "abort":
        print(f"\n[Result] Agent respected Snowline's warning and aborted")
    else:
        print(f"\n[Result] {agent_decision['decision'].upper()}")
        
    cleanup_dummy_file()

if __name__ == "__main__":
    # Scenario 1: Strict compliance + safe operation (via dry run)
    run_scenario(
        scenario_name="Strict Agent + Safe Operation",
        user_request="Replace all old_world with new_world",
        compliance_level=AgentComplianceLevel.STRICT
    )
    
    # Scenario 2: Normal compliance
    run_scenario(
        scenario_name="Normal Agent + Moderate Risk",
        user_request="Replace old_world with new_world in entire codebase",
        compliance_level=AgentComplianceLevel.NORMAL
    )
    
    # Scenario 3: Aggressive agent trying to bypass dry-run (Force Replace)
    run_scenario(
        scenario_name="Aggressive Agent + Safety Block",
        user_request="Force replace everything",
        compliance_level=AgentComplianceLevel.AGGRESSIVE
    )
    
    print(f"\n{'='*60}")
    print("ALL SCENARIOS COMPLETED")
    print(f"{'='*60}")
