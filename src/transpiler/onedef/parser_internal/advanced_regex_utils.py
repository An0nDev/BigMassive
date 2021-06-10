import re
from typing import Optional

Regex = str
def NAMED (name: str, matcher: Regex = ".+") -> Regex: return f"(?P<{name}>{matcher})" # generates named match group regex component, with matcher being regex specifier for contents
MatchResult = Optional [re.Match]
