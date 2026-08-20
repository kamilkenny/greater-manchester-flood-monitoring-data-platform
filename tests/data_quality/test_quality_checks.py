from flood_monitoring.validation.checks import (
    build_quality_report,
)


def test_zero_warnings_does_not_fail_quality():
    stations = [
        {
            "station_reference": "A1",
            "river_name": "River Test",
            "town": "Town",
            "latitude": 53.5,
            "longitude": -2.2,
        }
    ]

    measures = [
        {
            "measure_url": "https://example/M1",
        }
    ]

    readings = [
        {
            "measure_url": "https://example/M1",
            "reading_datetime": "2026-08-20T01:00:00Z",
            "value": 1.0,
        }
    ]

    report = build_quality_report(
        stations,
        measures,
        readings,
        [],
    )

    assert report["status"] == "PASSED"
    assert report["warning_rows"] == 0
