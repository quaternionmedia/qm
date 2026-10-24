"""The harness document names a private repository by its reference wherever it appears."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import harness_status  # noqa: E402


def test_a_private_name_in_another_repositorys_record_is_redacted():
    """Mutation: return `records` unchanged, and the base keeps the name."""
    roster = [{"name": "blorpling", "ref": "private-9"}, {"name": "qm"}]
    records = [{"name": "qm", "slots": {"open_prs": [{"number": 1, "base": "project/blorpling"}]}}]
    out = harness_status.redact_private(records, roster)
    assert out[0]["slots"]["open_prs"][0]["base"] == "project/private-9"
    assert out[0]["name"] == "qm"


def test_without_the_companion_nothing_is_rewritten():
    """A roster whose private entry carries only its reference has no name to replace."""
    roster = [{"name": "private-9", "ref": "private-9"}]
    records = [{"name": "qm", "note": "project/private-9"}]
    assert harness_status.redact_private(records, roster) == records
