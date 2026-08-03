import ast, sys, re

JS_PATTERNS = [
    r"function\s+\w+\s*\(",
    r"class\s+\w+",
]

def get_ranges(c):
    try:
        t = ast.parse(c)
        r = {}
        for n in ast.walk(t):
            if hasattr(n, "name"):
                r[n.name] = [n.lineno, n.end_lineno]
        return r
    except:
        return {}

def find_js_line(c, kw):
    lines = c.split("\n")
    for i, line in enumerate(lines):
        j = 0
        in_str = None
        while j < len(line):
            ch = line[j]
            if j > 0 and line[j-1] == "\\":
                j += 1
                continue
            if ch in "\"'":
                in_str = None if in_str == ch else ch
                j += 1
                continue
            if in_str:
                j += 1
                continue
            # Check if keyword found AND pattern matches
            if kw in line[:j]:
                for pat in JS_PATTERNS:
                    if re.search(pat, line[:j]):
                        return i
            j += 1
    return None

def extract_body(c, start):
    lines = c.split("\n")
    depth = 0
    paren_depth = 0
    body_started = False
    found = False
    i = start
    while True:
        if i >= len(lines):
            return None
        line = lines[i]
        j = 0
        in_str = None
        while j < len(line):
            ch = line[j]
            if in_str and j > 0 and line[j-1] == "\\":
                j += 1
                continue
            if ch in "\"'":
                in_str = None if in_str == ch else ch
                j += 1
                continue
            if in_str:
                j += 1
                continue
            if ch == "`":
                return None
            if ch == "/":
                return None
            if ch == "(":
                paren_depth += 1
            elif ch == ")":
                paren_depth -= 1
                if paren_depth == 0:
                    body_started = True
            if ch == "{":
                if body_started:
                    depth += 1
                    found = True
            elif ch == "}":
                if body_started:
                    depth -= 1
                    if depth < 0:
                        return None
                    if depth == 0 and found:
                        return (start, i)
            j += 1
        i += 1
    return None

def splice(fp, fn):
    try:
        with open(fp) as f:
            c = f.read()
    except Exception as e:
        sys.stderr.write(f"[ERROR] {e}\n")
        return
    lines = c.split("\n")
    if fp.endswith(".py"):
        res = get_ranges(c)
        if fn in res:
            s, e = res[fn]
            for i in range(s - 1, e):
                print(lines[i])
            return
    js_exts = [".js", ".jsx", ".ts", ".tsx"]
    if any(fp.endswith(ext) for ext in js_exts):
        start = find_js_line(c, fn)
        if start is not None:
            body = extract_body(c, start)
            if body:
                s, e = body
                for i in range(s, e + 1):
                    print(lines[i])
                return
    sys.stderr.write(f"[ERROR] {fn} not found\n")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        splice(sys.argv[1], sys.argv[2])
