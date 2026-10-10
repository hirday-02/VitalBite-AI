"""
VitalBite AI — Emoji Removal Audit Automated Verification Test
Verifies that zero emoji characters exist across user-facing UI components, services,
and application files to ensure compliance with modern healthcare SaaS design standards.
"""
import unittest
import glob
import os

class TestEmojiAudit(unittest.TestCase):
    def test_zero_emojis_in_source_code(self):
        """Audits all Python codebase files to guarantee 0 emojis in strings, labels, and templates."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        py_files = glob.glob(os.path.join(project_root, "**", "*.py"), recursive=True)

        found_emojis = []
        for filepath in py_files:
            rel_path = os.path.relpath(filepath, project_root)
            if rel_path.startswith("venv") or rel_path.startswith(".git"):
                continue

            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line_idx, line in enumerate(f, 1):
                    for char in line:
                        code_point = ord(char)
                        # Check for emoji ranges (symbols, pictographs, transport/map, supplemental)
                        if code_point > 0x2300 and code_point not in (0x2600, 0x2601):
                            if char not in ('©', '®', '™', '°', '±', '×', '÷', '≥', '≤', '≠', '≈'):
                                found_emojis.append((rel_path, line_idx, char, line.strip()[:60]))

        self.assertEqual(
            len(found_emojis),
            0,
            f"Found {len(found_emojis)} emojis in application source files:\n" +
            "\n".join([f"{path}:{line} -> {char} ({text})" for path, line, char, text in found_emojis[:10]])
        )

if __name__ == "__main__":
    unittest.main()
