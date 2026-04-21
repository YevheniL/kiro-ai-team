"""QA tests for weather_app.py"""
import unittest
from unittest.mock import patch, MagicMock
import requests
from weather_app import search_weather, on_search, WMO_CODES


# --- Fixtures ---

GEO_RESPONSE = {
    "results": [{
        "name": "London",
        "country": "United Kingdom",
        "latitude": 51.51,
        "longitude": -0.13,
    }]
}

FORECAST_RESPONSE = {
    "current_weather": {
        "temperature": 15.0,
        "windspeed": 10.0,
        "weathercode": 3,
        "time": "2026-04-15T14:00",
    },
    "hourly": {
        "time": ["2026-04-15T13:00", "2026-04-15T14:00", "2026-04-15T15:00"],
        "relative_humidity_2m": [60, 65, 70],
    },
}


def _mock_get_factory(geo=GEO_RESPONSE, forecast=FORECAST_RESPONSE):
    """Return a side_effect function for requests.get that serves geo then forecast."""
    call_count = {"n": 0}

    def _mock_get(url, **kwargs):
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        if call_count["n"] == 0:
            resp.json.return_value = geo
        else:
            resp.json.return_value = forecast
        call_count["n"] += 1
        return resp

    return _mock_get


# --- Unit Tests: search_weather ---

class TestSearchWeather(unittest.TestCase):

    @patch("weather_app.requests.get")
    def test_happy_path(self, mock_get):
        mock_get.side_effect = _mock_get_factory()
        result = search_weather("London")
        self.assertEqual(result["city"], "London, United Kingdom")
        self.assertEqual(result["temp"], 15.0)
        self.assertEqual(result["wind"], 10.0)
        self.assertEqual(result["code"], 3)
        self.assertEqual(result["humidity"], 65)

    @patch("weather_app.requests.get")
    def test_city_not_found(self, mock_get):
        mock_get.side_effect = _mock_get_factory(geo={"results": None})
        with self.assertRaises(ValueError) as ctx:
            search_weather("Nonexistent")
        self.assertIn("not found", str(ctx.exception))

    @patch("weather_app.requests.get")
    def test_city_not_found_empty_list(self, mock_get):
        mock_get.side_effect = _mock_get_factory(geo={"results": []})
        with self.assertRaises(ValueError):
            search_weather("Nonexistent")

    @patch("weather_app.requests.get")
    def test_city_not_found_no_key(self, mock_get):
        mock_get.side_effect = _mock_get_factory(geo={})
        with self.assertRaises(ValueError):
            search_weather("Nonexistent")

    @patch("weather_app.requests.get")
    def test_humidity_fallback_when_time_mismatch(self, mock_get):
        forecast = {
            "current_weather": {
                "temperature": 20.0, "windspeed": 5.0,
                "weathercode": 0, "time": "2026-04-15T14:30",  # half-hour — won't match
            },
            "hourly": {
                "time": ["2026-04-15T14:00", "2026-04-15T15:00"],
                "relative_humidity_2m": [50, 55],
            },
        }
        mock_get.side_effect = _mock_get_factory(forecast=forecast)
        result = search_weather("London")
        self.assertIsNone(result["humidity"])

    @patch("weather_app.requests.get")
    def test_humidity_fallback_missing_key(self, mock_get):
        forecast = {
            "current_weather": {
                "temperature": 20.0, "windspeed": 5.0,
                "weathercode": 0, "time": "2026-04-15T14:00",
            },
            "hourly": {"time": ["2026-04-15T14:00"]},  # no humidity key
        }
        mock_get.side_effect = _mock_get_factory(forecast=forecast)
        result = search_weather("London")
        self.assertIsNone(result["humidity"])

    @patch("weather_app.requests.get")
    def test_network_error_geo(self, mock_get):
        mock_get.side_effect = requests.ConnectionError("no network")
        with self.assertRaises(requests.ConnectionError):
            search_weather("London")

    @patch("weather_app.requests.get")
    def test_http_error_raises(self, mock_get):
        resp = MagicMock()
        resp.raise_for_status.side_effect = requests.HTTPError("500")
        mock_get.return_value = resp
        with self.assertRaises(requests.HTTPError):
            search_weather("London")

    @patch("weather_app.requests.get")
    def test_country_missing(self, mock_get):
        geo = {"results": [{"name": "Somewhere", "latitude": 0, "longitude": 0}]}
        mock_get.side_effect = _mock_get_factory(geo=geo)
        result = search_weather("Somewhere")
        self.assertEqual(result["city"], "Somewhere, ")


# --- Unit Tests: on_search ---

class TestOnSearch(unittest.TestCase):

    def _make_mocks(self, entry_text="London"):
        entry = MagicMock()
        entry.get.return_value = entry_text
        label = MagicMock()
        return entry, label

    @patch("weather_app.search_weather")
    def test_happy_path_display(self, mock_sw):
        mock_sw.return_value = {
            "city": "London, United Kingdom", "temp": 15.0,
            "wind": 10.0, "code": 3, "humidity": 65,
        }
        entry, label = self._make_mocks()
        on_search(entry, label)
        final_text = label.config.call_args_list[-1][1]["text"]
        self.assertIn("London", final_text)
        self.assertIn("15.0 °C", final_text)
        self.assertIn("65 %", final_text)
        self.assertNotIn("N/A", final_text)

    @patch("weather_app.search_weather")
    def test_humidity_none_shows_na(self, mock_sw):
        mock_sw.return_value = {
            "city": "London, United Kingdom", "temp": 15.0,
            "wind": 10.0, "code": 0, "humidity": None,
        }
        entry, label = self._make_mocks()
        on_search(entry, label)
        final_text = label.config.call_args_list[-1][1]["text"]
        self.assertIn("N/A", final_text)
        self.assertNotIn("None", final_text)

    def test_empty_input_does_nothing(self):
        entry, label = self._make_mocks("   ")
        on_search(entry, label)
        label.config.assert_not_called()

    @patch("weather_app.search_weather", side_effect=ValueError("City 'X' not found."))
    def test_city_not_found_message(self, _):
        entry, label = self._make_mocks("X")
        on_search(entry, label)
        final_text = label.config.call_args_list[-1][1]["text"]
        self.assertIn("not found", final_text)

    @patch("weather_app.search_weather", side_effect=requests.ConnectionError())
    def test_network_error_message(self, _):
        entry, label = self._make_mocks("London")
        on_search(entry, label)
        final_text = label.config.call_args_list[-1][1]["text"]
        self.assertIn("Network error", final_text)

    @patch("weather_app.search_weather", side_effect=RuntimeError("boom"))
    def test_unexpected_error_message(self, _):
        entry, label = self._make_mocks("London")
        on_search(entry, label)
        final_text = label.config.call_args_list[-1][1]["text"]
        self.assertIn("Unexpected error", final_text)

    def test_searching_feedback(self):
        """Verify 'Searching...' is shown before the API call."""
        entry, label = self._make_mocks("London")
        with patch("weather_app.search_weather", side_effect=ValueError("fail")):
            on_search(entry, label)
        first_config_text = label.config.call_args_list[0][1]["text"]
        self.assertEqual(first_config_text, "Searching...")
        label.update_idletasks.assert_called_once()

    def test_input_truncation(self):
        long_input = "A" * 200
        entry, label = self._make_mocks(long_input)
        with patch("weather_app.search_weather") as mock_sw:
            mock_sw.return_value = {
                "city": "A, X", "temp": 0, "wind": 0, "code": 0, "humidity": None,
            }
            on_search(entry, label)
            called_city = mock_sw.call_args[0][0]
            self.assertLessEqual(len(called_city), 100)


# --- WMO Codes ---

class TestWMOCodes(unittest.TestCase):

    def test_freezing_codes_present(self):
        for code in (56, 57, 66, 67):
            self.assertIn(code, WMO_CODES, f"WMO code {code} missing")

    def test_all_standard_codes_present(self):
        expected = {0, 1, 2, 3, 45, 48, 51, 53, 55, 56, 57, 61, 63, 65, 66, 67,
                    71, 73, 75, 77, 80, 81, 82, 85, 86, 95, 96, 99}
        self.assertEqual(set(WMO_CODES.keys()), expected)


if __name__ == "__main__":
    unittest.main()
