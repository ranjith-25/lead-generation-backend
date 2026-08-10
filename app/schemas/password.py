import re
from typing import Annotated

from pydantic import AfterValidator

PASSWORD_MIN_LENGTH = 8

_DIGIT = re.compile(r"\d")
_SYMBOL = re.compile(r"[^A-Za-z0-9\s]")


def validate_password_strength(value: str) -> str:

    problems: list[str] = []

    if len(value) < PASSWORD_MIN_LENGTH:
        problems.append(f"be at least {PASSWORD_MIN_LENGTH} characters long")

    if not _DIGIT.search(value):
        problems.append("contain at least one number")

    if not _SYMBOL.search(value):
        problems.append("contain at least one symbol")

    if problems:
        raise ValueError("Password must " + ", ".join(problems))

    return value

Password = Annotated[str, AfterValidator(validate_password_strength)]
