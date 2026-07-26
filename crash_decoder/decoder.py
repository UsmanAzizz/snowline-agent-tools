import os
import sys
import re

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def decode_crash(file_path):
    print("🚨 CRASH DECODER 🚨")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"[FAIL] File not found: {file_path}")
        return
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Common error identifiers
        error_lines = []
        stack_lines = []
        
        for line in content.split('\n'):
            line = line.strip()
            # Capture actual error messages
            if re.match(r'^(Error|TypeError|ReferenceError|SyntaxError|UnhandledPromiseRejectionWarning|Exception):', line, re.IGNORECASE):
                error_lines.append(line)
            # Capture stack trace lines
            elif line.startswith('at '):
                # Filter out node_modules and internal node scripts
                if 'node_modules' not in line and 'node:internal' not in line:
                    stack_lines.append(line)
            # Python tracebacks
            elif line.startswith('File "') and 'site-packages' not in line and 'Python\\' not in line:
                stack_lines.append(line)
                
        if not error_lines and not stack_lines:
            print("[WARN] No standard crash signature found in this log.")
            print("[INFO] Make sure you copy-pasted the entire stack trace.")
        else:
            print("[FAIL] CRASH DETECTED:\n")
            for e in error_lines[:3]: # limit to top 3 errors
                print(f"  ❌ {e}")
                
            if stack_lines:
                print("\n[INFO] RELEVANT SOURCE CODE TRACE (Noise Filtered):")
                for s in stack_lines[:5]: # limit to top 5 traces
                    print(f"  👉 {s}")
                    
            print("\n" + "=" * 60)
            print("💡 PROMPT UNTUK AI (Copy-Paste ini):")
            print('"Berdasarkan hasil Crash Decoder di atas, tolong gunakan tool view_file untuk memeriksa baris spesifik yang menyebabkan error tersebut, dan berikan solusinya."')
            
    except Exception as e:
        print(f"[FAIL] Could not read log file: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python decoder.py <path_to_error_log.txt>")
        sys.exit(1)
        
    decode_crash(sys.argv[1])

if __name__ == "__main__":
    main()
