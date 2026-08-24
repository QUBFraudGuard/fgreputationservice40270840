from unittest.mock import patch, Mock
import requests
import reputation_screening


def _mock_response(json_data):
    resp = Mock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


@patch("reputation_screening.requests.get")
def test_high_risk_score_is_flagged(mock_get):
    mock_get.return_value = _mock_response({"card": "5555", "risk_score": 95})
    result = reputation_screening.screen_transaction("5000-5555-UK")
    assert result["decision"] == "SUSPICIOUS"
    assert result["reason"] == "reputation score 95 exceeds threshold"


@patch("reputation_screening.requests.get")
def test_low_risk_score_passes(mock_get):
    mock_get.return_value = _mock_response({"card": "1234", "risk_score": 10})
    result = reputation_screening.screen_transaction("5000-1234-UK")
    assert result["decision"] == "OK"


@patch("reputation_screening.requests.get")
def test_score_exactly_at_threshold_passes(mock_get):
    mock_get.return_value = _mock_response({"card": "1234", "risk_score": 70})
    result = reputation_screening.screen_transaction("5000-1234-UK")
    assert result["decision"] == "OK"


@patch("reputation_screening.requests.get")
def test_score_one_above_threshold_is_flagged(mock_get):
    mock_get.return_value = _mock_response({"card": "1234", "risk_score": 71})
    result = reputation_screening.screen_transaction("5000-1234-UK")
    assert result["decision"] == "SUSPICIOUS"


@patch("reputation_screening.requests.get")
def test_network_failure_fails_closed(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout()
    result = reputation_screening.screen_transaction("5000-1234-UK")
    assert result["decision"] == "SUSPICIOUS"
    assert result["reason"] == "reputation check unavailable"


@patch("reputation_screening.requests.get")
def test_connection_error_fails_closed(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError()
    result = reputation_screening.screen_transaction("5000-1234-UK")
    assert result["decision"] == "SUSPICIOUS"
    assert result["reason"] == "reputation check unavailable"


@patch("reputation_screening.requests.get")
def test_bad_status_code_fails_closed(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_get.return_value = mock_response
    result = reputation_screening.screen_transaction("5000-1234-UK")
    assert result["decision"] == "SUSPICIOUS"
    assert result["reason"] == "reputation check unavailable"


@patch("reputation_screening.requests.get")
def test_malformed_response_missing_risk_score_fails_closed(mock_get):
    mock_get.return_value = _mock_response({"card": "1234"})
    result = reputation_screening.screen_transaction("5000-1234-UK")
    assert result["decision"] == "SUSPICIOUS"
    assert result["reason"] == "reputation response malformed"


def test_malformed_card_format_returns_error():
    result = reputation_screening.screen_transaction("5000-CARD-UK")
    assert result["decision"] == "ERROR"
    assert "invalid card format" in result["reason"]


def test_wrong_part_count_returns_error():
    result = reputation_screening.screen_transaction("5000-1234")
    assert result["decision"] == "ERROR"