import json
import subprocess

def run_cli(path):
    result = subprocess.run([
        "python", "-m", "rhaid_autofix", path, "--json"
    ], capture_output=True, text=True)
    return json.loads(result.stdout)

def test_unused_import():
    path = "examples/minimal_unused_import.py"
    out = run_cli(path)
    print("Unused import issues:", out['issues'])
    assert any(i['id'] == 'py:unused_import' for i in out['issues'])

def test_formatting():
    path = "examples/formatting_issue.py"
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        print("Actual file content (formatting):\n", f.read())
    import rhaid.rules
    print("Registered rules (formatting):", list(rhaid.rules._RULES.keys()))
    path = "examples/formatting_issue.py"
    import subprocess
    result = subprocess.run([
        "python", "-m", "rhaid_autofix", path, "--json"
    ], capture_output=True, text=True)
    print("Raw CLI output (formatting):", result.stdout)
    out = run_cli(path)
    print("Formatting issues:", out['issues'])
    # Accept any format:spacing or format:newline or format:crlf
    assert any(i['id'] in ('format:spacing', 'format:newline', 'format:crlf', 'format:tabs') for i in out['issues'])

def test_secrets():
    path = "examples/secret_key.py"
    out = run_cli(path)
    print("Secrets issues:", out['issues'])
    assert any(i['id'] == 'secrets:api_key' for i in out['issues'])

def test_markdown():
    path = "examples/markdown_heading.md"
    out = run_cli(path)
    print("Markdown issues:", out['issues'])
    assert any(i['id'] == 'md:heading_space' for i in out['issues'])

def test_json():
    path = "examples/json_in_comment.py"
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        print("Actual file content (json):\n", f.read())
    import rhaid.rules
    print("Registered rules (json):", list(rhaid.rules._RULES.keys()))
    path = "examples/json_in_comment.py"
    import subprocess
    result = subprocess.run([
        "python", "-m", "rhaid_autofix", path, "--json"
    ], capture_output=True, text=True)
    print("Raw CLI output (json):", result.stdout)
    out = run_cli(path)
    print("JSON issues:", out['issues'])
    assert any(i['id'] == 'json:object' for i in out['issues'])

def test_baseline():
    path = "examples/minimal_unused_import.py"
    # Write baseline
    subprocess.run(["python", "-m", "rhaid_autofix", path, "--write-baseline"])
    # Respect baseline
    result = subprocess.run([
        "python", "-m", "rhaid_autofix", path, "--respect-baseline", "--json"
    ], capture_output=True, text=True)
    out = json.loads(result.stdout)
    # Should suppress all issues
    print("Baseline issues:", out['issues'])
    assert out['issues'] == []
