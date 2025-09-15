from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RuleResult:
    """Represents a single rule result (issue)."""

    id: str
    message: str
    severity: str
    path: str
    line: Optional[int] = None
    col: Optional[int] = None


@dataclass
class FixResult:
    """Represents the result of applying a fixer."""

    applied: bool
    notes: List[str]
    content: str
