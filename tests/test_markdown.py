from rhaid.rules import run_rules
import rhaid.register_rules

rhaid.register_rules.register_all_rules()


def test_md_heading_and_fence(tmp_path):
    p = tmp_path / "doc.md"
    text = "#NoSpace\n" "## Has space\n" "```py\n" "# inside code #NoSpace\n" "```\n"
    issues = run_rules(str(p), text, {})
    hits = [i for i in issues if i.id == "md:heading_space"]
    assert len(hits) == 1 and hits[0].line == 1
    assert not [i for i in issues if i.id == "md:unclosed_fence"]


def test_md_unclosed_fence(tmp_path):
    p = tmp_path / "doc.md"
    text = "# Title\n```\ncode\n"
    issues = run_rules(str(p), text, {})
    assert any(i.id == "md:unclosed_fence" for i in issues)
