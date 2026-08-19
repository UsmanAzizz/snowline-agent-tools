import json

# Mock JSON output from `knip --reporter json`
MOCK_KNIP_JSON = """
{
  "files": {},
  "dependencies": {
    "react": [{"type": "dependency", "name": "react", "pos": 100}],
    "react-dom": [{"type": "dependency", "name": "react-dom", "pos": 200}],
    "lodash": [{"type": "dependency", "name": "lodash", "pos": 300}],
    "jest": [{"type": "devDependency", "name": "jest", "pos": 400}],
    "eslint": [{"type": "devDependency", "name": "eslint", "pos": 500}]
  },
  "unlisted": {},
  "binaries": {},
  "unresolved": {},
  "exports": {},
  "types": {},
  "enumMembers": {},
  "classMembers": {},
  "duplicates": {},
  "unusedFiles": [
    "src/components/old-button.tsx",
    "src/utils/deprecated-helpers.ts"
  ],
  "dependencies_metadata": {
    "executionTime": "120ms",
    "version": "1.0.0",
    "absolutePaths": true
  }
}
"""

def parse_knip_output(raw_json):
    """
    Cleans the Knip JSON output by keeping only non-empty keys that represent issues
    and removing unnecessary metadata.
    """
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}

    # Define keys that represent issues we want to report if they are not empty
    issue_keys = [
        "files", "dependencies", "unlisted", "binaries", "unresolved",
        "exports", "types", "enumMembers", "classMembers", "duplicates", "unusedFiles"
    ]

    cleaned_data = {}
    for key in issue_keys:
        if key in data:
            val = data[key]
            # Check if the value is a non-empty list or dict
            if isinstance(val, list) and len(val) > 0:
                cleaned_data[key] = val
            elif isinstance(val, dict) and len(val) > 0:
                # For dicts like 'dependencies', we might just want to list the names to save space
                cleaned_data[key] = list(val.keys())

    return cleaned_data

if __name__ == '__main__':
    print("--- Knip Static Tool Wrapper PoC ---")
    
    # Simulate a much larger string by duplicating dependencies
    large_mock_data = json.loads(MOCK_KNIP_JSON)
    for i in range(200):
        large_mock_data["dependencies"][f"mock-dep-{i}"] = [{"type": "dependency", "name": f"mock-dep-{i}", "pos": 1000 + i}]
    
    raw_large_json = json.dumps(large_mock_data)
    
    print(f"Original Character Length: {len(raw_large_json)}")
    
    parsed_output = parse_knip_output(raw_large_json)
    parsed_json_str = json.dumps(parsed_output, indent=2)
    
    print(f"Parsed Character Length: {len(parsed_json_str)}")
    print("\n--- Parsed Output ---")
    print(parsed_json_str)
