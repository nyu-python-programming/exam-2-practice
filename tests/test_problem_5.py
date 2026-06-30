"""
Do not run this file directly!  It won't work.
Run it using the Test panel in Visual Studio Code or by using the pytest command from the Terminal command line.
"""
from problem_5 import *


class Tests:
    @classmethod
    def mock_input(cls, mock_data, monkeypatch):
        """Mock the builtin input function to feed pre-set responses."""
        mock_data["inputs-copy"] = mock_data["inputs"].copy()

        def new_input(message):
            mock_data["actual-input-count"] += 1
            return mock_data["inputs-copy"].pop(0)

        monkeypatch.setattr("builtins.input", lambda x: new_input(x))

    def run_main(self, case, capsys, monkeypatch):
        Tests.mock_input(case, monkeypatch)
        try:
            main()
        except Exception as e:
            assert False, (
                f"Q5 - Program should not crash when given inputs {case['inputs']}, however it did: {e};"
            )
        return capsys.readouterr().out.strip()

    def test_name_not_found(self, capsys, monkeypatch):
        case = {"inputs": ["Foo Bar"], "actual-input-count": 0}
        output = self.run_main(case, capsys, monkeypatch)
        assert output.lower() == "name not found!", (
            f"Q5 - Expected 'Name not found!' for a name not in the data, instead got '{output}';"
        )

    def test_found_person_fields(self, capsys, monkeypatch):
        case = {"inputs": ["nevins bussel"], "actual-input-count": 0}
        output = self.run_main(case, capsys, monkeypatch).lower()
        assert "name: nevins bussel" in output, (
            f"Q5 - Expected the person's name in the output, instead got '{output}';"
        )
        assert "country: indonesia" in output, (
            f"Q5 - Expected the person's country in the output, instead got '{output}';"
        )
        assert "email: nbussel1@1688.com" in output, (
            f"Q5 - Expected the person's lowercased email in the output, instead got '{output}';"
        )

    def test_email_is_lowercased(self, capsys, monkeypatch):
        # In the data this email is stored as 'SKermannes0@rediff.com'.
        case = {"inputs": ["Starlene Kermannes"], "actual-input-count": 0}
        output = self.run_main(case, capsys, monkeypatch)
        assert "skermannes0@rediff.com" in output, (
            f"Q5 - Expected the email to be printed in all lowercase, instead got '{output}';"
        )
        assert "SKermannes0@rediff.com" not in output, (
            f"Q5 - The email should be lowercased, not printed as stored in the file;"
        )

    def test_case_insensitive_match(self, capsys, monkeypatch):
        case = {"inputs": ["NEVINS BUSSEL"], "actual-input-count": 0}
        output = self.run_main(case, capsys, monkeypatch).lower()
        assert "country: indonesia" in output, (
            f"Q5 - The name match should be case-insensitive, instead got '{output}';"
        )
