from snowline import SnowlineCompanion
import os

def run_demo():
    # Setup dummy file for testing
    with open("dummy_test.txt", "w") as f:
        f.write("Hello old_world!\nThis is a test of old_world.")

    companion = SnowlineCompanion()

    # Step 1: Agent tries to replace without dry_run (Unsafe request)
    print("--- 1. Agent Requests Execution without dry_run ---")
    unsafe_req = {
        "tool": "smart_replace",
        "params": {
            "pattern": "old_world",
            "replacement": "new_world",
            "scope_file": "dummy_test.txt",
            "dry_run": False
        }
    }
    
    # Companion intercepts and provides guidance (blocks it since it's risky)
    response_1 = companion.handle_request(unsafe_req)
    print(f"Status: {response_1['snowline_response']['status']}")
    print(f"Guidance Action: {response_1['snowline_response']['guidance']['action']}")
    print(f"Guidance Reason: {response_1['snowline_response']['guidance']['reason']}")
    print()

    # Step 2: Agent respects guidance, does a dry_run first
    print("--- 2. Agent Requests Preview (dry_run=True) ---")
    safe_req = {
        "tool": "smart_replace",
        "params": {
            "pattern": "old_world",
            "replacement": "new_world",
            "scope_file": "dummy_test.txt",
            "dry_run": True
        }
    }
    response_2 = companion.handle_request(safe_req)
    print(f"Status: {response_2['snowline_response']['status']}")
    print(f"Guidance Action: {response_2['snowline_response']['guidance']['action']}")
    print("Preview Data:", response_2['snowline_response']['dry_run']['preview'])
    print()

    # Step 3: Agent decides preview looks good, executes the actual replacement
    print("--- 3. Agent Executes Action ---")
    # We must explicitly pass dry_run: False to execute.
    safe_req["params"]["dry_run"] = False
    exec_result = companion.execute(safe_req)
    print("Execution Result:", exec_result)
    
    # Check if backup was created
    backup_id = exec_result.get("result", {}).get("backup_id")
    print(f"Backup created with ID: {backup_id}")
    
    with open("dummy_test.txt", "r") as f:
        print("\nFile content after replacement:")
        print(f.read())
        
    # Step 4: Agent triggers rollback
    if backup_id:
        print("\n--- 4. Agent Requests Rollback ---")
        tool = companion.registry.get_tool("smart_replace")
        rollback_res = tool.rollback(backup_id)
        print("Rollback Result:", rollback_res)
        
        with open("dummy_test.txt", "r") as f:
            print("\nFile content after rollback:")
            print(f.read())

    # Cleanup
    os.remove("dummy_test.txt")

if __name__ == "__main__":
    run_demo()
