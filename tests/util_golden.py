#!/usr/bin/env python3
"""
Golden diff printer - Item 5
On test fail, dump unified diff against last green artifacts/ci_smoke/chat.log
"""

import difflib
import pathlib

def udiff(a, b):
    """Return unified diff between two strings"""
    return "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True)))

def main():
    """Example usage of the golden diff utility"""
    # This would be used in test frameworks to compare against golden files
    print("Golden diff utility loaded")
    
    # Example usage:
    # golden_file = pathlib.Path("artifacts/ci_smoke/chat.log")
    # if golden_file.exists():
    #     with open(golden_file) as f:
    #         golden_content = f.read()
    #     current_content = "... current test output ..."
    #     diff = udiff(golden_content, current_content)
    #     if diff:
    #         print("DIFF against golden file:")
    #         print(diff)

if __name__ == "__main__":
    main()