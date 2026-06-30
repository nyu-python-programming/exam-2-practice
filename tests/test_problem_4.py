"""
Do not run this file directly!  It won't work.
Run it using the Test panel in Visual Studio Code or by using the pytest command from the Terminal command line.
"""
import re

from problem_4 import *


class Tests:
    def run_main(self, capsys):
        """Run the program and return its captured, stripped stdout."""
        try:
            main()
        except Exception as e:
            assert False, f"Q4 - Program should not crash, however it did: {e};"
        return capsys.readouterr().out.strip()

    def agency_count(self, output, agency):
        """
        Return the integer printed on the output line for the given agency, or
        None if no line for that agency is found. Tolerant of the amount of
        spacing the student uses between the two aligned columns.
        """
        pattern = re.compile(
            r"^" + re.escape(agency.upper()) + r"\s+(\d+)\s*$",
            re.IGNORECASE | re.MULTILINE,
        )
        match = pattern.search(output)
        return int(match.group(1)) if match else None

    def test_known_agency_counts(self, capsys):
        """A spot-check of entry-level counts for several agencies."""
        output = self.run_main(capsys)
        expected = {
            "DEPT OF ENVIRONMENT PROTECTION": 146,
            "DEPT OF PARKS & RECREATION": 87,
            "OFFICE OF MANAGEMENT & BUDGET": 82,
            "DEPT OF HEALTH/MENTAL HYGIENE": 55,
            "NYC HOUSING AUTHORITY": 54,
            "DEPARTMENT OF CORRECTION": 36,
            "POLICE DEPARTMENT": 6,
        }
        for agency, count in expected.items():
            actual = self.agency_count(output, agency)
            assert actual is not None, (
                f"Q4 - Expected a line for agency '{agency}' in the output, but none was found;"
            )
            assert actual == count, (
                f"Q4 - Expected {count} entry-level jobs for '{agency}', instead got {actual};"
            )

    def test_agency_names_uppercase(self, capsys):
        """Agency names in the output must be uppercase."""
        output = self.run_main(capsys)
        assert "DEPT OF PARKS & RECREATION" in output, (
            "Q4 - Expected agency names to be printed in uppercase;"
        )
        assert "Dept of Parks & Recreation" not in output, (
            "Q4 - Agency names should be uppercase, not title/mixed case;"
        )

    def test_all_agencies_listed_once(self, capsys):
        """Every agency that has entry-level jobs should appear exactly once."""
        output = self.run_main(capsys)
        # 36 distinct agencies in the data have at least one Entry-Level job.
        agencies = [
            "DEPT OF ENVIRONMENT PROTECTION",
            "DEPT OF PARKS & RECREATION",
            "OFFICE OF MANAGEMENT & BUDGET",
            "DEPT OF HEALTH/MENTAL HYGIENE",
            "NYC HOUSING AUTHORITY",
            "DEPARTMENT OF CORRECTION",
            "DEPARTMENT OF TRANSPORTATION",
            "LAW DEPARTMENT",
        ]
        for agency in agencies:
            occurrences = len(
                re.findall(
                    r"^" + re.escape(agency) + r"\s+\d+\s*$",
                    output,
                    re.MULTILINE,
                )
            )
            assert occurrences == 1, (
                f"Q4 - Expected agency '{agency}' to be listed exactly once, "
                f"instead it appeared {occurrences} times;"
            )
