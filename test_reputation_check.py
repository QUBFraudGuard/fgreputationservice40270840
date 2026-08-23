# test_reputation_check.py
from unittest.mock import patch, Mock
import requests
import reputation_check


def _mock_response(json_data):
    resp = Mock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@patch("reputation_check.requests.get")
def test_high_risk_score_is_flagged(mock_get):
    mock_get.return_value = _mock_response({"card": "5555", "risk_score": 95})

    result = reputation_check.check({"card": "5555"})

    assert result is not None
    assert result["reason"] == "reputation score 95 exceeds threshold"


@patch("reputation_check.requests.get")
def test_low_risk_score_passes(mock_get):
    mock_get.return_value = _mock_response({"card": "1234", "risk_score": 10})

    result = reputation_check.check({"card": "1234"})

    assert result is None


@patch("reputation_check.requests.get")
def test_score_exactly_at_threshold_passes(mock_get):
    mock_get.return_value = _mock_response({"card": "1234", "risk_score": 70})

    result = reputation_check.check({"card": "1234"})

    assert result is None


@patch("reputation_check.requests.get")
def test_score_one_above_threshold_is_flagged(mock_get):
    mock_get.return_value = _mock_response({"card": "1234", "risk_score": 71})

    result = reputation_check.check({"card": "1234"})

    assert result is not None


@patch("reputation_check.requests.get")
def test_network_failure_fails_closed(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout()

    result = reputation_check.check({"card": "1234"})

    assert result is not None
    assert result["reason"] == "reputation check unavailable"


@patch("reputation_check.requests.get")
def test_connection_error_fails_closed(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError()

    result = reputation_check.check({"card": "1234"})

    assert result is not None
    assert result["reason"] == "reputation check unavailable"


@patch("reputation_check.requests.get")
def test_bad_status_code_fails_closed(mock_get):
    # simulate raise_for_status() actually raising, e.g. a 500 from the service
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_get.return_value = mock_response

    result = reputation_check.check({"card": "1234"})

    assert result is not None
    assert result["reason"] == "reputation check unavailable"


@patch("reputation_check.requests.get")
def test_malformed_response_missing_risk_score_fails_closed(mock_get):
    mock_get.return_value = _mock_response({"card": "1234"})  # no risk_score key

    result = reputation_check.check({"card": "1234"})

    assert result is not None
    assert result["reason"] == "reputation response malformed"


@patch("reputation_check.requests.get")
def test_missing_card_key_does_not_crash(mock_get):
    mock_get.return_value = _mock_response({"card": "", "risk_score": 10})

    result = reputation_check.check({})  # no "card" key at all

    assert result is None