from flood_monitoring.ingestion.transforms import (
    normalise_measures,
    normalise_readings,
    normalise_stations,
    normalise_warnings,
)


def test_normalise_station():
    rows = normalise_stations(
        [
            {
                "stationReference": "A1",
                "label": "Example",
                "riverName": "River Test",
                "town": "Test Town",
                "lat": 53.5,
                "long": -2.2,
                "status": "Active",
            }
        ]
    )

    assert rows[0]["station_reference"] == "A1"
    assert rows[0]["river_name"] == "River Test"


def test_measure_and_reading_join():
    station_payload = [
        {
            "stationReference": "A1",
            "measures": [
                {
                    "@id": "https://example/measures/M1",
                    "parameter": "level",
                    "parameterName": "Water Level",
                    "qualifier": "Stage",
                    "unitName": "m",
                    "period": 900,
                }
            ],
        }
    ]

    measures = normalise_measures(station_payload)

    readings = normalise_readings(
        [
            {
                "measure": "https://example/measures/M1",
                "dateTime": "2026-08-20T01:00:00Z",
                "date": "2026-08-20",
                "value": 1.25,
            }
        ],
        measures,
    )

    assert len(readings) == 1
    assert readings[0]["station_reference"] == "A1"
    assert readings[0]["value"] == 1.25


def test_non_local_reading_is_removed():
    readings = normalise_readings(
        [
            {
                "measure": "https://example/measures/OUTSIDE",
                "value": 10,
            }
        ],
        [],
    )

    assert readings == []


def test_empty_warning_payload_is_valid():
    assert normalise_warnings([]) == []
