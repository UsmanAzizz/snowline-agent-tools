import json

MOCK_SEMGREP_OUTPUT = """
{
  "errors": [],
  "paths": {
    "scanned": [
      "app/main.py"
    ]
  },
  "results": [
    {
      "check_id": "python.flask.security.audit.render-template-string.render-template-string",
      "end": {
        "col": 44,
        "line": 15,
        "offset": 450
      },
      "extra": {
        "engine_kind": "OSS",
        "fingerprint": "1234567890abcdef",
        "is_ignored": false,
        "lines": "    return render_template_string(template)",
        "message": "Found user-controlled data being passed to render_template_string(). This could lead to a Server-Side Template Injection (SSTI) vulnerability. An attacker could potentially execute arbitrary code on the server. Ensure that user input is properly sanitized or use pre-defined templates with safe variable substitution.",
        "metadata": {
          "cwe": [
            "CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')"
          ],
          "impact": "HIGH",
          "likelihood": "HIGH",
          "owasp": [
            "A03:2021 - Injection"
          ],
          "references": [
            "https://owasp.org/www-community/attacks/Server_Side_Template_Injection"
          ],
          "vulnerability_class": [
            "Cross-Site-Scripting (XSS)"
          ]
        },
        "metavars": {},
        "severity": "ERROR"
      },
      "path": "app/main.py",
      "start": {
        "col": 12,
        "line": 15,
        "offset": 418
      }
    },
    {
      "check_id": "python.lang.security.audit.exec-use.exec-use",
      "end": {
        "col": 30,
        "line": 42,
        "offset": 1050
      },
      "extra": {
        "engine_kind": "OSS",
        "fingerprint": "fedcba0987654321",
        "is_ignored": false,
        "lines": "    exec(user_provided_code)",
        "message": "Use of exec() is dangerous and can lead to arbitrary code execution if the input is untrusted. Consider alternatives such as evaluating the expression safely or sandboxing the execution environment completely.",
        "metadata": {
          "cwe": [
            "CWE-94: Improper Control of Generation of Code ('Code Injection')"
          ],
          "impact": "HIGH",
          "likelihood": "LOW",
          "owasp": [
            "A03:2021 - Injection"
          ],
          "references": [
            "https://docs.python.org/3/library/functions.html#exec"
          ],
          "vulnerability_class": [
            "Code Injection"
          ]
        },
        "metavars": {},
        "severity": "WARNING"
      },
      "path": "app/main.py",
      "start": {
        "col": 5,
        "line": 42,
        "offset": 1025
      }
    }
  ],
  "version": "1.30.0"
}
"""

def parse_semgrep_output(raw_json_str):
    data = json.loads(raw_json_str)
    parsed_results = []
    
    for result in data.get("results", []):
        path = result.get("path")
        start_line = result.get("start", {}).get("line")
        check_id = result.get("check_id")
        message = result.get("extra", {}).get("message", "")
        
        parsed_results.append({
            "path": path,
            "start.line": start_line,
            "check_id": check_id,
            "message": message[:50]
        })
        
    return parsed_results

if __name__ == '__main__':
    print(f"Original length (chars): {len(MOCK_SEMGREP_OUTPUT)}")
    
    parsed = parse_semgrep_output(MOCK_SEMGREP_OUTPUT)
    parsed_str = json.dumps(parsed, indent=2)
    
    print(f"Parsed length (chars): {len(parsed_str)}")
    print("Parsed output:")
    print(parsed_str)
