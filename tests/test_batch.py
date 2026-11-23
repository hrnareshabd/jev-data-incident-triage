import json
from dataclasses import asdict
from unittest.mock import Mock

import pytest
from test_enrichment import make_incident

from jev_incident_triage import cli
from jev_incident_triage.batch import load_incidents
from jev_incident_triage.models import Incident


def write_batch(tmp_path, data):
    path = tmp_path / "incidents.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.mark.parametrize("field", [
    "failed_rows", "total_rows", "retry_count", "elapsed_minutes", "sla_minutes",
])
@pytest.mark.parametrize("value", [-1, True, 1.5, "1", None])
def test_rejects_invalid_numeric_fields(field, value):
    with pytest.raises(ValueError, match=field):
        make_incident(**{field: value})


@pytest.mark.parametrize("field", ["incident_id", "pipeline", "environment", "error_message"])
@pytest.mark.parametrize("value", ["", "  ", None, 42])
def test_rejects_invalid_text_fields(field, value):
    with pytest.raises(ValueError, match=field):
        make_incident(**{field: value})


@pytest.mark.parametrize("value", ["impact", [""], [None], [1], None])
def test_rejects_invalid_impact(value):
    with pytest.raises(ValueError, match="business_impact"):
        make_incident(business_impact=value)


def test_zero_counts_and_empty_impact_are_valid():
    assert make_incident(failed_rows=0, total_rows=0, business_impact=[]).total_rows == 0


def test_failed_rows_cannot_exceed_total():
    with pytest.raises(ValueError, match="exceed"):
        make_incident(failed_rows=101)


@pytest.mark.parametrize("change, message", [
    (lambda d: d.pop("pipeline"), "missing fields: pipeline"),
    (lambda d: d.update(extra=1), "unknown fields: extra"),
])
def test_schema_errors(change, message):
    data = asdict(make_incident())
    change(data)
    with pytest.raises(ValueError, match=message):
        Incident.from_dict(data)


@pytest.mark.parametrize("data", [{}, "text", 3, None])
def test_batch_requires_array(tmp_path, data):
    with pytest.raises(ValueError, match="JSON array"):
        load_incidents(write_batch(tmp_path, data))


def test_batch_rejects_duplicate_ids(tmp_path):
    data = asdict(make_incident())
    with pytest.raises(ValueError, match="incident 2: duplicate incident_id"):
        load_incidents(write_batch(tmp_path, [data, data]))


def test_batch_preserves_order_and_accepts_empty_list(tmp_path):
    data = [asdict(make_incident(incident_id=value)) for value in ["B", "A"]]
    assert [i.incident_id for i in load_incidents(write_batch(tmp_path, data))] == ["B", "A"]
    assert load_incidents(write_batch(tmp_path, [])) == []


def test_invalid_later_record_makes_no_inference_calls(tmp_path, monkeypatch, capsys):
    path = write_batch(tmp_path, [asdict(make_incident()), {"error_message": "private evidence"}])
    inference = Mock()
    monkeypatch.setattr(cli, "triage_incident", inference)
    monkeypatch.setattr("sys.argv", ["jev-triage", str(path)])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
    inference.assert_not_called()
    output = capsys.readouterr()
    assert output.out == ""
    assert "incident 2: missing fields" in output.err
    assert "private evidence" not in output.err


@pytest.mark.parametrize("contents", ["{", "[null]", "[1]"])
def test_cli_reports_invalid_json_or_records(tmp_path, monkeypatch, capsys, contents):
    path = tmp_path / "invalid.json"
    path.write_text(contents)
    monkeypatch.setattr("sys.argv", ["jev-triage", str(path)])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
    assert "Invalid incident batch:" in capsys.readouterr().err


def test_valid_batch_calls_inference_and_prints_json(tmp_path, monkeypatch, capsys):
    path = write_batch(tmp_path, [asdict(make_incident())])
    result = Mock()
    result.as_dict.return_value = {"incident_id": "INC-TEST", "action": "escalate"}
    inference = Mock(return_value=result)
    monkeypatch.setattr(cli, "triage_incident", inference)
    monkeypatch.setattr("sys.argv", ["jev-triage", str(path)])
    cli.main()
    inference.assert_called_once()
    assert inference.call_args.args[0].sla_breached is True
    assert json.loads(capsys.readouterr().out) == [result.as_dict.return_value]


@pytest.mark.parametrize("contents", [None, b"\xff"])
def test_unreadable_input_exits_cleanly(tmp_path, monkeypatch, capsys, contents):
    path = tmp_path / "input.json"
    if contents is not None:
        path.write_bytes(contents)
    monkeypatch.setattr("sys.argv", ["jev-triage", str(path)])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert "Invalid incident batch:" in output.err


def test_empty_batch_makes_no_inference_calls(tmp_path, monkeypatch, capsys):
    path = write_batch(tmp_path, [])
    inference = Mock()
    monkeypatch.setattr(cli, "triage_incident", inference)
    monkeypatch.setattr("sys.argv", ["jev-triage", str(path)])
    cli.main()
    inference.assert_not_called()
    assert json.loads(capsys.readouterr().out) == []
