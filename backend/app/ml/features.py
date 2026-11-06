import re
from typing import Dict, List


class CodeFeatureExtractor:
    """
    Static Code Feature Extraction Engine
    Parses C/C++ source code to extract a 16-dimensional numerical descriptor vector
    characterizing computational intensity, memory patterns, and control-flow structure.
    """

    @classmethod
    def extract_features(cls, code: str) -> Dict[str, float]:
        # Strip string literals and character constants to avoid false positives
        cleaned_code = re.sub(r'"(\\.|[^"\\])*"', '""', code)
        cleaned_code = re.sub(r"'(\\.|[^'\\])*'", "''", cleaned_code)
        
        # Remove single-line comments
        cleaned_code = re.sub(r"//.*", "", cleaned_code)
        # Remove multi-line comments
        cleaned_code = re.sub(r"/\*[\s\S]*?\*/", "", cleaned_code)

        lines = [line.strip() for line in cleaned_code.splitlines() if line.strip()]
        loc = len(lines)

        # 1. Structural features
        func_count = len(re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_*]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^;{}]*\)\s*\{", cleaned_code))
        if func_count == 0 and "main" in cleaned_code:
            func_count = 1

        # 2. Loops and maximum nesting depth
        loop_count = len(re.findall(r"\b(for|while|do)\b", cleaned_code))
        max_loop_nesting = cls._calculate_max_loop_nesting(cleaned_code)

        # 3. Cyclomatic Complexity: branches + 1
        branch_matches = len(re.findall(r"\b(if|else\s+if|case|default|while|for|catch)\b|\?|&&|\|\|", cleaned_code))
        cyclomatic_complexity = branch_matches + 1

        # 4. Arithmetic Operations
        # Integer ops: +, -, *, /, % (excluding pointer dereferences or increments)
        int_ops = len(re.findall(r"(?<=[a-zA-Z0-9_])\s*(\+|\-|\*|\/|\%)\s*(?=[a-zA-Z0-9_])", cleaned_code))
        
        # Floating point: detect float/double constants or keywords
        float_keywords = len(re.findall(r"\b(float|double)\b", cleaned_code))
        float_literals = len(re.findall(r"\b\d+\.\d+[fF]?\b", cleaned_code))
        float_ops = (float_keywords * 2) + float_literals

        # 5. Memory & Pointer Indirections
        ptr_derefs = len(re.findall(r"->|\*(?=[a-zA-Z_])|&(?=[a-zA-Z_])", cleaned_code))
        array_subscripts = len(re.findall(r"\[[^\]]+\]", cleaned_code))

        # 6. Control Flow
        branch_count = len(re.findall(r"\b(if|else|switch|case)\b", cleaned_code))
        
        # 7. Recursion (function calling itself)
        recursive_calls = cls._count_recursive_calls(cleaned_code)

        # 8. Bitwise operations: &, |, ^, ~, <<, >>
        bitwise_ops = len(re.findall(r"(<<|>>|~|\^|&|\|)(?!=)", cleaned_code))

        # 9. Dynamic Memory Allocations
        memory_allocs = len(re.findall(r"\b(malloc|calloc|realloc|free|new|delete)\b", cleaned_code))

        # 10. Math Library Calls
        math_calls = len(re.findall(r"\b(sin|cos|tan|sqrt|pow|exp|log|fabs|ceil|floor)\b", cleaned_code))

        # 11. Global Variables (declarations outside any braces)
        global_vars = cls._count_global_vars(cleaned_code)

        # 12. Arithmetic to Branch Ratio
        total_arithmetic = int_ops + float_ops
        arithmetic_to_branch_ratio = round((total_arithmetic / (branch_count + 1)), 2)

        return {
            "lines_of_code": float(loc),
            "function_count": float(func_count),
            "cyclomatic_complexity": float(cyclomatic_complexity),
            "loop_count": float(loop_count),
            "max_loop_nesting_depth": float(max_loop_nesting),
            "integer_arithmetic_ops": float(int_ops),
            "float_arithmetic_ops": float(float_ops),
            "pointer_dereferences": float(ptr_derefs),
            "array_subscript_ops": float(array_subscripts),
            "branch_count": float(branch_count),
            "recursive_call_count": float(recursive_calls),
            "bitwise_ops": float(bitwise_ops),
            "memory_allocation_ops": float(memory_allocs),
            "math_library_calls": float(math_calls),
            "global_variable_count": float(global_vars),
            "arithmetic_to_branch_ratio": float(arithmetic_to_branch_ratio),
        }

    @staticmethod
    def _calculate_max_loop_nesting(code: str) -> int:
        """
        Calculates the deepest loop nesting depth, handling both braced
        and unbraced (single-statement) nested loop hierarchies.
        """
        # Simplify loop headers by removing their ( ... ) condition/iteration clause
        cleaned = re.sub(r"\bfor\s*\([^)]*\)", " LOOP_KEYWORD ", code)
        cleaned = re.sub(r"\bwhile\s*\([^)]*\)", " LOOP_KEYWORD ", cleaned)
        cleaned = re.sub(r"\bdo\b", " LOOP_KEYWORD ", cleaned)

        tokens = re.findall(r"LOOP_KEYWORD|[\{\};]", cleaned)
        max_depth = 0
        current_depth = 0
        loop_stack: List[str] = []

        for t in tokens:
            if t == "LOOP_KEYWORD":
                current_depth += 1
                if current_depth > max_depth:
                    max_depth = current_depth
                loop_stack.append("pending")
            elif t == "{":
                if loop_stack and loop_stack[-1] == "pending":
                    loop_stack[-1] = "braced"
                else:
                    loop_stack.append("other_brace")
            elif t == "}":
                if loop_stack:
                    kind = loop_stack.pop()
                    if kind == "braced":
                        current_depth = max(0, current_depth - 1)
            elif t == ";":
                while loop_stack and loop_stack[-1] == "pending":
                    loop_stack.pop()
                    current_depth = max(0, current_depth - 1)

        return max_depth

    @staticmethod
    def _count_recursive_calls(code: str) -> int:
        """Finds functions that call their own identifier."""
        # Find function definitions
        func_matches = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^;{}]*\)\s*\{([^}]*)\}", code)
        recursive_count = 0
        for name, body in func_matches:
            if name != "main" and re.search(rf"\b{name}\s*\(", body):
                recursive_count += 1
        return recursive_count

    @staticmethod
    def _count_global_vars(code: str) -> int:
        """Counts variable declarations located outside function bodies."""
        outside_braces = []
        depth = 0
        current_chunk = []
        for char in code:
            if char == "{":
                if depth == 0 and current_chunk:
                    outside_braces.append("".join(current_chunk))
                    current_chunk = []
                depth += 1
            elif char == "}":
                depth = max(0, depth - 1)
            elif depth == 0:
                current_chunk.append(char)
        if current_chunk:
            outside_braces.append("".join(current_chunk))

        globals_text = " ".join(outside_braces)
        # Match standard variable definitions (e.g. int x = 10; double arr[100];)
        matches = re.findall(r"\b(int|double|float|char|long|short)\s+[a-zA-Z_][a-zA-Z0-9_]*\s*(\[[^\]]*\])?\s*(=|;)", globals_text)
        return len(matches)
