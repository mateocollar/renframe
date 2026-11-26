# RenFrame - Style and Architecture Guide (`CODING_STYLE.md`)

This document defines the mandatory rules for developing the **RenFrame** transpiler in Python.

Its goal is to keep the project simple, predictable, fast, and easy to maintain. When a design decision is not covered by this document, always choose the simplest, most explicit, and most direct option.

---

## 1. Core Philosophy

1. **One way to do things.**
   There is one accepted way to solve each problem, both in the DSL syntax and in the transpiler code. Do not add alternatives, shortcuts, optional configurations, or “tricks” for the same use case.

2. **Linear readability.**
   The flow must be readable from top to bottom. Unnecessary control-flow jumps, hidden metaprogramming, complex inheritance, and abstractions that force readers to inspect many files to understand a simple operation are prohibited.

3. **Clarity over brevity.**
   Readability takes priority over conciseness. A clear multi-line block is preferable to a compact but hard-to-understand expression.

4. **Explicit over implicit.**
   Names, types, errors, and behavior must be declared directly. Do not use magic, reflection, or hidden behavior to solve common problems.

5. **Fail fast.**
   If the input is invalid, ambiguous, or a macro does not exist, the transpiler must fail immediately with a clear error. Do not attempt to guess the user’s intent.

---

## 2. Dependencies and Environment

- The transpiler core uses **only the Python standard library**.
- Allowed dependencies in the core:
  - `re`
  - `pathlib`
  - `json`
  - `argparse`
  - `dataclasses`
  - `typing`
- Frameworks, ORMs, web servers, and third-party libraries are not allowed in the core.
- If an external library is strictly necessary for a development tool, it must be justified in the `README` and must not be part of the transpiler pipeline.
- Minimum supported version: **Python 3.10+**.
- Use of `match/case`, `list[str]`, `dict[str, X]`, `X | None`, and other modern typing features available in Python 3.10 is allowed.

---

## 3. Project Structure

The structure must remain flat and predictable. Do not create folders or modules “just in case”.

```text
...(boring burocratic files)
pyproject.toml
renframe/
├── __init__.py
├── __main__.py
├── cli.py
├── lexer.py
├── parser.py
├── ast_nodes.py
├── macro_expander.py
├── transpiler.py
├── errors.py
└── tokens.py
```

Rules:

- `lexer.py`: converts source text into tokens.
- `parser.py`: converts tokens into an AST.
- `ast_nodes.py`: defines AST nodes.
- `macro_expander.py`: expands text-substitution macros and returns a clean AST.
- `transpiler.py`: converts a validated AST into Ren'Py code.
- `errors.py`: defines all DSL exceptions.
- `cli.py`: receives arguments, runs the pipeline, and displays errors to the user.
- `__main__.py`: only invokes the CLI entry point.

Generic module names such as `utils.py`, `helpers.py`, `common.py`, or `core.py` are not allowed. If a function does not have a clear home, it probably belongs to an existing pipeline phase or should not exist yet.

---

## 4. Data Flow

The transpiler operates as a one-way pipeline:

```text
.rf file
    │
    ▼
Lexer
    │
    ▼
Tokens
    │
    ▼
Parser
    │
    ▼
AST
    │
    ▼
MacroExpander
    │
    ▼
Expanded and validated AST
    │
    ▼
Transpiler
    │
    ▼
.rpy file
```

Mandatory rules:

- Each phase receives a clearly defined input and returns a clearly defined output.
- The Lexer does not know about screens, macros, or Ren'Py.
- The Parser does not generate Ren'Py code.
- The MacroExpander does not read files or execute transpilation logic.
- The Transpiler receives only an already-expanded and validated AST.
- A phase must not directly modify the internal state of another phase.
- Global mutable state cannot be shared between phases.
- The final output must be deterministic `.rpy` text: the same `.rf` file with the same configuration always produces the same `.rpy` output.

---

## 5. Python Code Conventions

### 5.1 Base style

- Follow **PEP 8**.
- Use **4-space** indentation.
- Use double quotes for strings: `"text"`.
- Lines must not exceed **100 characters**.
- Every file must end with a newline.
- Do not use wildcard imports (`from module import *`).
- Do not use ambiguous relative imports; use absolute imports within the package.

Correct example:

```python
from renframe.lexer import Lexer
from renframe.errors import RenFrameSyntaxError
```

### 5.2 Naming

| Element | Convention | Example |
|---|---|---|
| Variables | `snake_case` | `current_token` |
| Functions | `snake_case` | `tokenize_line` |
| Modules | `snake_case` | `macro_expander.py` |
| Classes | `PascalCase` | `ScreenNode` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_MACRO_DEPTH` |
| Internal attributes and methods | `_` prefix | `_advance_token()` |
| Exceptions | `PascalCase`, ending in `Error` | `MacroNotFoundError` |

### 5.3 Static typing

All functions, methods, and class attributes must include explicit type hints.

```python
# Correct
def tokenize_line(line: str, line_number: int) -> list[Token]:
    ...
```

```python
# Incorrect
def tokenize_line(line, line_number):
    ...
```

Rules:

- Do not use `Any` unless it is strictly unavoidable and justified with a comment.
- Use `X | None` for optional values, not `Optional[X]`.
- Use modern collection types: `list[str]`, `dict[str, int]`, `tuple[int, int]`.
- AST data types are defined in `ast_nodes.py`.
- Do not create unnecessary type aliases.

### 5.4 Dataclasses

For pure data structures, such as tokens and AST nodes, use:

```python
@dataclass(frozen=True)
class ScreenNode:
    name: str
    body: list[StatementNode]
```

Rules:

- Use `@dataclass(frozen=True)` whenever possible.
- If a node must be mutable during a phase, document why and use a normal `@dataclass`.
- Do not add methods with complex logic to AST nodes.
- AST nodes represent data, not transpiler behavior.

---

## 6. Functions and Classes

- Each function performs one clear task.
- As a guideline, a function must not exceed **30 to 40 lines**.
- If a function needs more than 40 lines, split it into functions with explicit names.
- Do not create classes when a simple function is enough.
- Do not use abstract classes, interfaces, or multiple inheritance unless there is a real, justified need.
- Do not use custom decorators.
- Do not use reflection, dynamic `getattr`, or automatic function registration.
- Do not use mutable global variables.
- Declare constants in the module where they are used.

Preferred example:

```python
def parse_screen(tokens: list[Token], index: int) -> tuple[ScreenNode, int]:
    ...
```

Avoid:

```python
class ScreenParserFactory:
    ...
```

Unless there is a concrete and evident reason.

---

## 7. Error Handling

The transpiler must fail fast and provide useful messages.

### 7.1 Allowed exceptions

All DSL exceptions are defined in `errors.py`:

- `RenFrameError`
- `RenFrameSyntaxError`
- `MacroNotFoundError`
- `ImportResolutionError`
- `TranspilerError`

`RenFrameError` is the base class for all custom exceptions.

### 7.2 Rules

- Throwing `Exception`, `ValueError`, `RuntimeError`, or other generic exceptions for DSL errors is prohibited.
- Every custom exception must include:
  - Source file.
  - Line number.
  - Clear message.
- The message must explain what failed and, when possible, what was expected.
- Do not catch exceptions to hide errors.
- Do not use empty `try/except` blocks.
- Do not use `except Exception` except at the CLI boundary, to convert an internal error into a readable final message.

Example:

```python
raise RenFrameSyntaxError(
    file_path=file_path,
    line_number=token.line,
    message=f"Expected 'end', but found '{token.value}'.",
)
```

---

## 8. Tests

- Each pipeline phase must have independent tests:
  - Lexer.
  - Parser.
  - MacroExpander.
  - Transpiler.
  - CLI.
- Every DSL error must have at least one test.
- Each test must verify observable behavior, not internal implementation details.
- Tests use small, representative `.rf` files.
- Do not write tests that depend on the execution order of other tests.
- Do not use mocks unless they are necessary to isolate the filesystem or CLI.

---

## 9. Documentation and Comments

- Code should explain itself.
- Do not write comments that repeat what the code already says.

Incorrect:

```python
# Increment the index
index += 1
```

Correct:

```python
# Advance after consuming the current token.
index += 1
```

- Comments explain intent, constraints, or edge cases.
- Every public module must have a one- or two-line docstring.
- Every public class must have a brief docstring.
- Do not document dead code; remove unnecessary code.
- Do not leave context-free `TODO` comments. If a `TODO` exists, it must state what is missing and why.

---

## 10. Decision Rules

When facing a design decision, apply this order:

1. Choose the simplest solution.
2. Choose the most explicit solution.
3. Choose the solution with the fewest states and branches.
4. Choose the solution that requires the fewest new files.
5. Choose the solution that produces the clearest errors.
6. Only then consider an abstraction.

Add an abstraction only when:

- At least two real use cases need it.
- It removes significant duplication.
- It makes the code easier to read.
- It does not hide the program’s main flow.

If it does not meet those conditions, write the code directly.

---

## 11. Prohibitions

The following are prohibited:

- Adding external dependencies to the core.
- Creating multiple ways to do the same thing.
- Using hidden metaprogramming.
- Using complex inheritance.
- Using `Any` without justification.
- Using generic exceptions for DSL errors.
- Using mutable global variables.
- Creating circular imports.
- Creating `utils`, `helpers`, `common`, or `core` modules.
- Leaving dead or commented-out code.
- Adding optional configuration without a real need.
- Optimizing before measuring.
- Adding functionality “just in case”.