"""
Coding Style Learner for Ergo Work Mode
Learns and tracks coding preferences from user interactions
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class CodingStyleLearner:
    """Learns coding preferences and style patterns from user interactions"""

    def __init__(self, db_path: str = "~/ergo/runtime/missions.db"):
        self.db_path = Path(db_path).expanduser()
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def learn_from_accepted_suggestion(
        self,
        language: str,
        pattern_type: str,
        pattern: str,
        confidence: float = 0.7
    ):
        """Learn from user accepting a code suggestion"""
        self._update_or_create_preference(
            language=language,
            category="accepted_patterns",
            preference_key=pattern_type,
            preference_value=pattern,
            confidence=confidence,
            source="accepted_suggestion"
        )

    def learn_from_manual_edit(
        self,
        language: str,
        before_code: str,
        after_code: str,
        edit_type: str
    ):
        """Learn from user manually editing agent-generated code"""
        # Analyze what changed
        changes = self._analyze_code_diff(before_code, after_code)

        for change in changes:
            self._update_or_create_preference(
                language=language,
                category="manual_corrections",
                preference_key=f"{edit_type}_{change['type']}",
                preference_value=json.dumps(change),
                confidence=0.8,
                source="manual_edit"
            )

    def learn_from_review_feedback(
        self,
        language: str,
        feedback_type: str,
        pattern: str,
        severity: str = "warning"
    ):
        """Learn from code review feedback patterns"""
        confidence = {
            "critical": 1.0,
            "error": 0.9,
            "warning": 0.7,
            "info": 0.5
        }.get(severity, 0.6)

        self._update_or_create_preference(
            language=language,
            category="review_patterns",
            preference_key=feedback_type,
            preference_value=pattern,
            confidence=confidence,
            source="review_feedback"
        )

    def learn_from_codebase_analysis(
        self,
        project_id: str,
        language: str,
        patterns: Dict[str, Any]
    ):
        """Learn from analyzing existing codebase patterns"""
        for pattern_type, pattern_value in patterns.items():
            self._update_or_create_preference(
                language=language,
                category="codebase_patterns",
                preference_key=pattern_type,
                preference_value=json.dumps(pattern_value),
                confidence=0.6,
                source=f"codebase:{project_id}",
                project_id=project_id
            )

    def get_preferences_for_language(self, language: str) -> Dict[str, Any]:
        """Get all coding preferences for a language"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM coding_style_preferences
            WHERE language = ?
            ORDER BY confidence DESC, times_applied DESC
        """, (language,))

        prefs = [dict(row) for row in cursor.fetchall()]

        # Group by category
        grouped = {}
        for pref in prefs:
            category = pref['category']
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(pref)

        return grouped

    def get_preference(
        self,
        language: str,
        category: str,
        preference_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific preference"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM coding_style_preferences
            WHERE language = ? AND category = ? AND preference_key = ?
        """, (language, category, preference_key))

        row = cursor.fetchone()
        return dict(row) if row else None

    def apply_preference(
        self,
        language: str,
        category: str,
        preference_key: str,
        success: bool = True
    ):
        """Record that a preference was applied"""
        cursor = self.conn.cursor()

        # Increment times_applied
        cursor.execute("""
            UPDATE coding_style_preferences
            SET times_applied = times_applied + 1,
                last_applied = ?
            WHERE language = ? AND category = ? AND preference_key = ?
        """, (datetime.now().isoformat(), language, category, preference_key))

        # If successful, increase confidence slightly
        if success:
            cursor.execute("""
                UPDATE coding_style_preferences
                SET confidence = MIN(1.0, confidence + 0.05)
                WHERE language = ? AND category = ? AND preference_key = ?
            """, (language, category, preference_key))

        self.conn.commit()

    def reject_preference(
        self,
        language: str,
        category: str,
        preference_key: str
    ):
        """Record that user rejected a preference"""
        cursor = self.conn.cursor()

        # Decrease confidence
        cursor.execute("""
            UPDATE coding_style_preferences
            SET confidence = MAX(0.0, confidence - 0.2),
                updated_at = ?
            WHERE language = ? AND category = ? AND preference_key = ?
        """, (datetime.now().isoformat(), language, category, preference_key))

        self.conn.commit()

    def get_style_summary(self, language: str) -> Dict[str, Any]:
        """Get a summary of learned style preferences for a language"""
        cursor = self.conn.cursor()

        # Get high-confidence preferences
        cursor.execute("""
            SELECT category, preference_key, preference_value, confidence, times_applied
            FROM coding_style_preferences
            WHERE language = ? AND confidence >= 0.7
            ORDER BY confidence DESC, times_applied DESC
            LIMIT 20
        """, (language,))

        high_confidence = [dict(row) for row in cursor.fetchall()]

        # Get statistics
        cursor.execute("""
            SELECT
                COUNT(*) as total_preferences,
                AVG(confidence) as avg_confidence,
                SUM(times_applied) as total_applications
            FROM coding_style_preferences
            WHERE language = ?
        """, (language,))

        stats = dict(cursor.fetchone())

        return {
            "language": language,
            "high_confidence_preferences": high_confidence,
            "statistics": stats,
            "generated_at": datetime.now().isoformat()
        }

    def generate_style_guide(self, language: str) -> str:
        """Generate a markdown style guide from learned preferences"""
        summary = self.get_style_summary(language)
        prefs_by_category = self.get_preferences_for_language(language)

        md = f"# {language.title()} Coding Style Guide\n\n"
        md += f"**Generated**: {summary['generated_at']}\n"
        md += f"**Total Preferences**: {summary['statistics']['total_preferences']}\n"
        md += f"**Average Confidence**: {summary['statistics']['avg_confidence']:.2f}\n\n"

        for category, prefs in prefs_by_category.items():
            if not prefs:
                continue

            md += f"## {category.replace('_', ' ').title()}\n\n"

            for pref in prefs[:10]:  # Top 10 per category
                md += f"### {pref['preference_key']}\n\n"
                md += f"**Confidence**: {pref['confidence']:.2f} | "
                md += f"**Applied**: {pref['times_applied']} times\n\n"

                # Try to parse value as JSON, fall back to string
                try:
                    value = json.loads(pref['preference_value'])
                    md += f"```json\n{json.dumps(value, indent=2)}\n```\n\n"
                except (json.JSONDecodeError, TypeError):
                    md += f"```\n{pref['preference_value']}\n```\n\n"

        return md

    def export_style_guide(self, language: str, output_path: Optional[Path] = None) -> Path:
        """Export style guide to markdown file"""
        if not output_path:
            output_path = Path(f"~/ergo/vault/coding-styles/{language.lower()}-style.md").expanduser()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        style_guide = self.generate_style_guide(language)
        output_path.write_text(style_guide)

        return output_path

    def _update_or_create_preference(
        self,
        language: str,
        category: str,
        preference_key: str,
        preference_value: str,
        confidence: float,
        source: str,
        project_id: Optional[str] = None
    ):
        """Update existing preference or create new one"""
        cursor = self.conn.cursor()

        # Check if exists
        existing = self.get_preference(language, category, preference_key)

        if existing:
            # Update with weighted average of confidence
            new_confidence = (existing['confidence'] + confidence) / 2

            cursor.execute("""
                UPDATE coding_style_preferences
                SET preference_value = ?,
                    confidence = ?,
                    source = ?,
                    updated_at = ?
                WHERE language = ? AND category = ? AND preference_key = ?
            """, (
                preference_value,
                new_confidence,
                source,
                datetime.now().isoformat(),
                language,
                category,
                preference_key
            ))
        else:
            # Create new
            cursor.execute("""
                INSERT INTO coding_style_preferences (
                    language, category, preference_key, preference_value,
                    confidence, source, project_id, times_applied
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                language, category, preference_key, preference_value,
                confidence, source, project_id, 0
            ))

        self.conn.commit()

    def _analyze_code_diff(self, before: str, after: str) -> List[Dict[str, Any]]:
        """Analyze differences between before and after code"""
        changes = []

        # Simple analysis - could be enhanced with AST parsing
        before_lines = before.split('\n')
        after_lines = after.split('\n')

        # Check for indentation changes
        before_indent = self._detect_indentation(before_lines)
        after_indent = self._detect_indentation(after_lines)

        if before_indent != after_indent:
            changes.append({
                "type": "indentation",
                "before": before_indent,
                "after": after_indent
            })

        # Check for naming convention changes
        before_names = self._extract_identifiers(before)
        after_names = self._extract_identifiers(after)

        for b_name, a_name in zip(before_names, after_names):
            if b_name != a_name and self._same_semantic_name(b_name, a_name):
                changes.append({
                    "type": "naming_convention",
                    "before": b_name,
                    "after": a_name,
                    "convention": self._detect_naming_convention(a_name)
                })

        return changes

    def _detect_indentation(self, lines: List[str]) -> str:
        """Detect indentation style (spaces vs tabs)"""
        for line in lines:
            if line.startswith('    '):
                return "4_spaces"
            elif line.startswith('  '):
                return "2_spaces"
            elif line.startswith('\t'):
                return "tabs"
        return "unknown"

    def _extract_identifiers(self, code: str) -> List[str]:
        """Extract identifier names from code (simple regex-based)"""
        import re
        # Very basic - could use language-specific parsers
        return re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code)

    def _same_semantic_name(self, name1: str, name2: str) -> bool:
        """Check if two names are semantically the same (just different casing)"""
        return name1.lower().replace('_', '') == name2.lower().replace('_', '')

    def _detect_naming_convention(self, name: str) -> str:
        """Detect naming convention of an identifier"""
        if name.isupper():
            return "SCREAMING_SNAKE_CASE"
        elif '_' in name and name.islower():
            return "snake_case"
        elif '_' in name:
            return "UPPER_SNAKE_CASE"
        elif name[0].isupper() and any(c.isupper() for c in name[1:]):
            return "PascalCase"
        elif name[0].islower() and any(c.isupper() for c in name[1:]):
            return "camelCase"
        else:
            return "lowercase"

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Example usage
if __name__ == "__main__":
    learner = CodingStyleLearner()

    # Learn from accepted suggestion
    learner.learn_from_accepted_suggestion(
        language="python",
        pattern_type="function_naming",
        pattern="snake_case",
        confidence=0.8
    )

    # Learn from codebase analysis
    learner.learn_from_codebase_analysis(
        project_id="ergo",
        language="python",
        patterns={
            "indentation": "4_spaces",
            "quote_style": "double_quotes",
            "line_length": 100,
            "import_order": "stdlib,third_party,local"
        }
    )

    # Get preferences
    prefs = learner.get_preferences_for_language("python")
    print(f"Learned {len(prefs)} Python preferences")

    # Generate style guide
    style_guide_path = learner.export_style_guide("python")
    print(f"Style guide exported to: {style_guide_path}")

    learner.close()
