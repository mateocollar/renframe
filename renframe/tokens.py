"""Token definition and TokenType enumeration for RenFrame."""

from dataclasses import dataclass
from enum import Enum, auto

class TokenType(Enum):
    """Enumeration of all valid token types in RenFrame."""

    #Keywords
    SCREEN = auto()
    MACRO  = auto()
    IMPORT = auto()
    IF     = auto()
    ELSE   = auto()
    FOR    = auto()
    IN     = auto()

    # Literals & identifiers
    IDENTIFIER = auto()
    STRING     = auto()
    NUMBER     = auto()
    BOOLEAN    = auto()

    # Symbols and punctuation
    AT       = auto()    # @ (for macros)
    COLON    = auto()    # :
    COMMA    = auto()    # ,
    LPAREN   = auto()    # (
    RPAREN   = auto()    # )
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]
    LBRACE   = auto()    # {
    RBRACE   = auto()    # }

   #Structural/Formatting
    INDENT  = auto()
    DEDENT  = auto()
    NEWLINE = auto()
    EOF     = auto()

@dataclass(frozen=True)
class Token:
    """Represents a single lexical token with position tracking for error reporting."""

    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)!s}, line={self.line}, col={self.column})"
