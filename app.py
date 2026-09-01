from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dash_table, dcc, html
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

load_dotenv(BASE_DIR / ".env")

from flood_monitoring.dashboard.data import (  # noqa: E402
    get_current_river_stations,
    get_river_history,
    get_river_names,
    load_dashboard_snapshot,
)


APP_TITLE = "Greater Manchester Flood & River Intelligence"
REFRESH_MS = 300_000


def _safe_number(value, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "—"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(number) >= 1000:
        return f"{number:,.0f}"
    return f"{number:.{digits}f}"


def _safe_int(value) -> str:
    if value is None or pd.isna(value):
        return "0"
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return "0"


def _safe_text(value, fallback: str = "Not available") -> str:
    if value is None or pd.isna(value):
        return fallback
    text = str(value).strip()
    return text or fallback


def _format_timestamp(value) -> str:
    if value is None or pd.isna(value):
        return "Not available"
    timestamp = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(timestamp):
        return _safe_text(value)
    return timestamp.strftime("%d %b %Y, %H:%M UTC")


def _empty_figure(message: str) -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font={"size": 15, "color": "#8da2b7"},
    )
    figure.update_layout(
        template=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 30, "r": 30, "t": 30, "b": 30},
        xaxis={"visible": False},
        yaxis={"visible": False},
    )
    return figure


def _chart_layout(
    title: str | None = None,
    *,
    height: int = 360,
    showlegend: bool = False,
) -> dict:
    return {
        "title": {
            "text": title or "",
            "x": 0.01,
            "xanchor": "left",
            "font": {"size": 16, "color": "#f4f8fc"},
        },
        "height": height,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "Inter, system-ui, sans-serif", "color": "#dce9f5"},
        "margin": {"l": 45, "r": 25, "t": 52, "b": 45},
        "showlegend": showlegend,
        "hoverlabel": {
            "bgcolor": "#0d2032",
            "bordercolor": "#33536d",
            "font": {"color": "#ffffff"},
        },
        "xaxis": {
            "showgrid": False,
            "zeroline": False,
            "linecolor": "rgba(141,162,183,0.18)",
            "tickfont": {"color": "#8da2b7"},
        },
        "yaxis": {
            "gridcolor": "rgba(141,162,183,0.10)",
            "zeroline": False,
            "tickfont": {"color": "#8da2b7"},
        },
    }


def _metric_card(
    label: str,
    value_id: str,
    detail_id: str,
    icon: str,
    tone: str,
) -> html.Div:
    return html.Div(
        className=f"metric-card {tone}",
        children=[
            html.Div(
                className="metric-topline",
                children=[
                    html.Span(icon, className="metric-icon"),
                    html.Span(label, className="metric-label"),
                ],
            ),
            html.Div("—", id=value_id, className="metric-value"),
            html.Div("Waiting for live data", id=detail_id, className="metric-detail"),
        ],
    )


def _section_heading(
    eyebrow: str,
    title: str,
    description: str,
) -> html.Div:
    return html.Div(
        className="section-heading",
        children=[
            html.Div(eyebrow, className="section-eyebrow"),
            html.H2(title),
            html.P(description),
        ],
    )


def _architecture_node(label: str, caption: str) -> html.Div:
    return html.Div(
        className="architecture-node",
        children=[
            html.Strong(label),
            html.Span(caption),
        ],
    )


def build_station_map(current: pd.DataFrame) -> go.Figure:
    if current.empty:
        return _empty_figure(
            "Station locations will appear when live data is available."
        )

    frame = current.copy()
    frame["Latitude"] = pd.to_numeric(frame.get("Latitude"), errors="coerce")
    frame["Longitude"] = pd.to_numeric(frame.get("Longitude"), errors="coerce")
    frame = frame.dropna(subset=["Latitude", "Longitude"])

    if frame.empty:
        return _empty_figure(
            "No geocoded monitoring stations are available."
        )

    frame = (
        frame.sort_values("ReadingDateTimeUTC")
        .drop_duplicates(subset=["StationKey"], keep="last")
        .copy()
    )

    status = (
        frame.get("CurrentStatus", pd.Series("", index=frame.index))
        .fillna("")
        .astype(str)
        .str.upper()
    )

    frame["MapStatus"] = "Normal"
    frame.loc[status.str.contains("ELEVATED"), "MapStatus"] = "Elevated"
    frame.loc[status.str.contains("ABOVE"), "MapStatus"] = "Above typical"

    styles = {
        "Normal": ("#087E8B", 8),
        "Elevated": ("#D59A32", 13),
        "Above typical": ("#B93A3A", 16),
    }

    figure = go.Figure()

    for status_name in ("Normal", "Elevated", "Above typical"):
        subset = frame[frame["MapStatus"] == status_name]

        if subset.empty:
            continue

        colour, size = styles[status_name]

        customdata = [
            [
                _safe_text(row.get("StationName")),
                _safe_text(row.get("RiverName")),
                _safe_text(row.get("Town")),
                _safe_number(row.get("CurrentValue")),
                _safe_text(row.get("UnitName"), ""),
                _safe_text(row.get("CurrentStatus")),
            ]
            for _, row in subset.iterrows()
        ]

        figure.add_trace(
            go.Scattermap(
                lat=subset["Latitude"],
                lon=subset["Longitude"],
                mode="markers",
                name=status_name,
                marker={
                    "size": size,
                    "color": colour,
                    "opacity": 0.88,
                },
                customdata=customdata,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "%{customdata[1]} · %{customdata[2]}<br><br>"
                    "Latest: %{customdata[3]} %{customdata[4]}<br>"
                    "Condition: %{customdata[5]}"
                    "<extra></extra>"
                ),
            )
        )

    figure.update_layout(
        map={
            "style": "carto-positron",
            "center": {
                "lat": float(frame["Latitude"].mean()),
                "lon": float(frame["Longitude"].mean()),
            },
            "zoom": 8.45,
        },
        height=500,
        margin={"l": 0, "r": 0, "t": 10, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend={
            "orientation": "h",
            "y": 1.02,
            "x": 0,
            "font": {"size": 11, "color": "#3E565B"},
            "bgcolor": "rgba(255,255,255,0.90)",
        },
        font={
            "family": "Inter, Segoe UI, sans-serif",
            "color": "#12262B",
        },
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "font": {"color": "#12262B"},
            "bordercolor": "#DCE5E2",
        },
    )

    return figure


def build_rainfall_chart(rainfall: pd.DataFrame) -> go.Figure:
    if rainfall.empty:
        return _empty_figure(
            "Rainfall observations will appear after the next successful refresh."
        )

    frame = rainfall.copy()

    frame["CurrentValue"] = pd.to_numeric(
        frame["CurrentValue"],
        errors="coerce",
    )

    frame = (
        frame.dropna(subset=["CurrentValue"])
        .sort_values("CurrentValue", ascending=False)
        .head(12)
        .copy()
    )

    if frame.empty:
        return _empty_figure(
            "No rainfall values are available."
        )

    labels = (
        frame["StationName"]
        .fillna("Unknown station")
        .astype(str)
    )

    colours = []

    for rank in range(len(frame)):
        if rank < 3:
            colours.append("#087E8B")
        elif rank < 7:
            colours.append("#27A7B8")
        else:
            colours.append("#9CCFD4")

    figure = go.Figure(
        go.Bar(
            x=frame["CurrentValue"],
            y=labels,
            orientation="h",
            marker={
                "color": colours,
                "line": {
                    "color": "rgba(8,126,139,0.15)",
                    "width": 1,
                },
            },
            text=[
                f"{value:.2f}"
                for value in frame["CurrentValue"]
            ],
            textposition="outside",
            textfont={
                "color": "#3E565B",
                "size": 10,
            },
            customdata=frame[
                ["Town", "UnitName"]
            ].fillna("").values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "%{customdata[0]}<br><br>"
                "Latest rainfall: %{x:.2f} %{customdata[1]}"
                "<extra></extra>"
            ),
        )
    )

    median_value = frame["CurrentValue"].median()

    if pd.notna(median_value):
        figure.add_vline(
            x=float(median_value),
            line_width=1,
            line_dash="dot",
            line_color="#8AA09D",
        )

    figure.update_layout(
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        margin={
            "l": 10,
            "r": 44,
            "t": 18,
            "b": 42,
        },
        bargap=0.32,
        showlegend=False,
        font={
            "family": "Inter, Segoe UI, sans-serif",
            "color": "#12262B",
        },
        xaxis={
            "title": "Latest rainfall reading",
            "showgrid": True,
            "gridcolor": "#E7EEEC",
            "zeroline": False,
            "tickfont": {
                "color": "#617276",
                "size": 10,
            },
        },
        yaxis={
            "autorange": "reversed",
            "showgrid": False,
            "tickfont": {
                "color": "#31494D",
                "size": 11,
            },
        },
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "font": {
                "color": "#12262B",
            },
            "bordercolor": "#DCE5E2",
        },
    )

    return figure


def build_warning_chart(warnings: pd.DataFrame) -> go.Figure:
    if warnings.empty:
        return _empty_figure(
            "Flood warning summary is not currently available."
        )

    frame = warnings.copy()

    frame["WarningCount"] = pd.to_numeric(
        frame["WarningCount"],
        errors="coerce",
    ).fillna(0)

    frame = frame[frame["WarningCount"] >= 0].copy()

    if frame.empty:
        return _empty_figure(
            "No warning summary records are available."
        )

    if "SeverityLevel" in frame.columns:
        frame["SeverityLevel"] = pd.to_numeric(
            frame["SeverityLevel"],
            errors="coerce",
        )

        frame = frame.sort_values(
            ["SeverityLevel", "WarningCount"],
            ascending=[True, False],
        )

    colours = []

    for severity in frame["Severity"].fillna("").astype(str):
        text_value = severity.lower()

        if "severe" in text_value:
            colours.append("#9F2929")
        elif "warning" in text_value:
            colours.append("#C96832")
        elif "alert" in text_value:
            colours.append("#D59A32")
        else:
            colours.append("#557A55")

    figure = go.Figure(
        go.Bar(
            x=frame["WarningCount"],
            y=frame["Severity"],
            orientation="h",
            marker={
                "color": colours,
                "line": {
                    "color": "rgba(18,38,43,0.08)",
                    "width": 1,
                },
            },
            text=frame["WarningCount"].astype(int),
            textposition="outside",
            textfont={
                "color": "#12262B",
                "size": 13,
            },
            hovertemplate=(
                "<b>%{y}</b><br>"
                "%{x} current warning records"
                "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        height=330,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        margin={
            "l": 10,
            "r": 48,
            "t": 16,
            "b": 38,
        },
        bargap=0.36,
        showlegend=False,
        font={
            "family": "Inter, Segoe UI, sans-serif",
            "color": "#12262B",
        },
        xaxis={
            "title": "Current records",
            "showgrid": True,
            "gridcolor": "#EEE6E2",
            "zeroline": False,
            "tickfont": {
                "color": "#617276",
                "size": 10,
            },
        },
        yaxis={
            "autorange": "reversed",
            "showgrid": False,
            "tickfont": {
                "color": "#31494D",
                "size": 11,
            },
        },
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "font": {
                "color": "#12262B",
            },
            "bordercolor": "#E5D7D1",
        },
    )

    return figure


def build_river_history_chart(
    river_name: str | None,
    history: pd.DataFrame,
) -> go.Figure:
    if not river_name:
        return _empty_figure(
            "Choose a river to explore its recent level history."
        )

    if history.empty:
        return _empty_figure(
            f"No historical level readings were returned for {river_name}."
        )

    frame = history.copy()

    frame["ReadingDateTimeUTC"] = pd.to_datetime(
        frame["ReadingDateTimeUTC"],
        errors="coerce",
        utc=True,
    )

    frame["ReadingValue"] = pd.to_numeric(
        frame["ReadingValue"],
        errors="coerce",
    )

    frame["TypicalRangeLow"] = pd.to_numeric(
        frame.get("TypicalRangeLow"),
        errors="coerce",
    )

    frame["TypicalRangeHigh"] = pd.to_numeric(
        frame.get("TypicalRangeHigh"),
        errors="coerce",
    )

    frame = frame.dropna(
        subset=[
            "ReadingDateTimeUTC",
            "ReadingValue",
        ]
    ).sort_values("ReadingDateTimeUTC")

    if frame.empty:
        return _empty_figure(
            f"No valid historical level readings were returned for {river_name}."
        )

    figure = go.Figure()

    palette = [
        "#087E8B",
        "#557A55",
        "#27A7B8",
        "#766A8A",
        "#9B704A",
        "#3F6E73",
    ]

    station_groups = list(
        frame.groupby("StationName", dropna=False)
    )

    for index, (station_name, station_frame) in enumerate(station_groups):
        station_frame = (
            station_frame
            .tail(400)
            .sort_values("ReadingDateTimeUTC")
            .copy()
        )

        colour = palette[index % len(palette)]

        valid_low = station_frame["TypicalRangeLow"].dropna()
        valid_high = station_frame["TypicalRangeHigh"].dropna()

        if not valid_low.empty and not valid_high.empty:
            typical_low = float(valid_low.median())
            typical_high = float(valid_high.median())

            if typical_high > typical_low:
                x_values = station_frame["ReadingDateTimeUTC"]

                figure.add_trace(
                    go.Scatter(
                        x=x_values,
                        y=[typical_high] * len(station_frame),
                        mode="lines",
                        line={"width": 0},
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

                figure.add_trace(
                    go.Scatter(
                        x=x_values,
                        y=[typical_low] * len(station_frame),
                        mode="lines",
                        line={"width": 0},
                        fill="tonexty",
                        fillcolor="rgba(39,167,184,0.055)",
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

        figure.add_trace(
            go.Scatter(
                x=station_frame["ReadingDateTimeUTC"],
                y=station_frame["ReadingValue"],
                mode="lines",
                name=_safe_text(
                    station_name,
                    "Unknown station",
                ),
                line={
                    "width": 2.5,
                    "color": colour,
                },
                hovertemplate=(
                    "<b>%{fullData.name}</b><br>"
                    "%{x|%d %b %Y, %H:%M}<br>"
                    "River level: %{y:.3f}"
                    "<extra></extra>"
                ),
            )
        )

        latest = station_frame.iloc[-1]

        figure.add_trace(
            go.Scatter(
                x=[latest["ReadingDateTimeUTC"]],
                y=[latest["ReadingValue"]],
                mode="markers",
                marker={
                    "size": 10,
                    "color": colour,
                    "line": {
                        "color": "#FFFFFF",
                        "width": 2,
                    },
                },
                hovertemplate=(
                    "<b>Latest observation</b><br>"
                    "%{x|%d %b %Y, %H:%M}<br>"
                    "%{y:.3f}"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )

    figure.update_layout(
        title={
            "text": f"{river_name} · recent level observations",
            "x": 0,
            "xanchor": "left",
            "font": {
                "size": 15,
                "color": "#12262B",
            },
        },
        height=440,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        margin={
            "l": 58,
            "r": 25,
            "t": 68,
            "b": 52,
        },
        hovermode="x unified",
        font={
            "family": "Inter, Segoe UI, sans-serif",
            "color": "#12262B",
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {
                "size": 10,
                "color": "#4B6266",
            },
        },
        xaxis={
            "showgrid": False,
            "zeroline": False,
            "linecolor": "#DCE5E2",
            "tickfont": {
                "color": "#617276",
                "size": 10,
            },
        },
        yaxis={
            "title": "River level",
            "showgrid": True,
            "gridcolor": "#E7EEEC",
            "gridwidth": 1,
            "zeroline": False,
            "linecolor": "#DCE5E2",
            "tickfont": {
                "color": "#617276",
                "size": 10,
            },
        },
        hoverlabel={
            "bgcolor": "#FFFFFF",
            "font": {
                "color": "#12262B",
            },
            "bordercolor": "#DCE5E2",
        },
    )

    return figure


def build_high_level_table(frame: pd.DataFrame) -> list[dict]:
    if frame.empty:
        return []

    result = frame.copy().head(12)
    result["ReadingDateTimeUTC"] = result["ReadingDateTimeUTC"].map(_format_timestamp)
    result["CurrentValue"] = result["CurrentValue"].map(lambda value: _safe_number(value, 3))
    result["TypicalRangeHigh"] = result["TypicalRangeHigh"].map(
        lambda value: _safe_number(value, 3)
    )
    result = result.rename(
        columns={
            "StationName": "Station",
            "RiverName": "River",
            "Town": "Town",
            "ReadingDateTimeUTC": "Observed",
            "CurrentValue": "Level",
            "TypicalRangeHigh": "Typical high",
            "CurrentStatus": "Status",
        }
    )

    columns = [
        "Station",
        "River",
        "Town",
        "Level",
        "Typical high",
        "Status",
        "Observed",
    ]
    return result[[column for column in columns if column in result.columns]].to_dict("records")


def build_station_table(frame: pd.DataFrame) -> list[dict]:
    if frame.empty:
        return []

    result = frame.copy()
    result["ReadingDateTimeUTC"] = result["ReadingDateTimeUTC"].map(_format_timestamp)
    for column in (
        "CurrentValue",
        "PreviousValue",
        "AbsoluteChange",
        "TypicalRangeLow",
        "TypicalRangeHigh",
    ):
        if column in result.columns:
            result[column] = result[column].map(lambda value: _safe_number(value, 3))

    result = result.rename(
        columns={
            "StationName": "Station",
            "Town": "Town",
            "CurrentValue": "Latest",
            "PreviousValue": "Previous",
            "AbsoluteChange": "Change",
            "UnitName": "Unit",
            "TypicalRangeLow": "Typical low",
            "TypicalRangeHigh": "Typical high",
            "CurrentStatus": "Status",
            "ReadingDateTimeUTC": "Observed",
        }
    )

    columns = [
        "Station",
        "Town",
        "Latest",
        "Unit",
        "Change",
        "Typical low",
        "Typical high",
        "Status",
        "Observed",
    ]
    return result[[column for column in columns if column in result.columns]].to_dict("records")


def summarise_etl(etl: pd.DataFrame) -> tuple[str, str, str, str, str]:
    if etl.empty:
        return (
            "UNKNOWN",
            "No ETL execution record available",
            "—",
            "—",
            "Pipeline history is unavailable",
        )

    latest = etl.iloc[0]
    status = _safe_text(latest.get("Status"), "UNKNOWN").upper()
    refreshed = _format_timestamp(latest.get("EndTimeUTC") or latest.get("StartTimeUTC"))
    rows_loaded = _safe_int(latest.get("RowsLoaded"))
    duration = _safe_number(latest.get("DurationSeconds"), 1)
    duration_text = "—" if duration == "—" else f"{duration} seconds"

    if status in {"SUCCEEDED", "SUCCESS", "COMPLETED"}:
        message = "Latest governed refresh completed successfully"
    else:
        error = _safe_text(latest.get("ErrorMessage"), "")
        message = error or "Latest pipeline execution requires attention"

    return status, refreshed, rows_loaded, duration_text, message


DATA_TABLE_STYLE = {
    "style_table": {
        "overflowX": "auto",
        "border": "none",
        "backgroundColor": "transparent",
    },
    "style_header": {
        "backgroundColor": "#0d2032",
        "color": "#9fb2c6",
        "fontWeight": "600",
        "border": "none",
        "borderBottom": "1px solid rgba(150,188,220,0.16)",
        "padding": "12px 13px",
        "textTransform": "uppercase",
        "fontSize": "11px",
        "letterSpacing": "0.06em",
    },
    "style_cell": {
        "backgroundColor": "rgba(8,20,32,0.52)",
        "color": "#dce9f5",
        "border": "none",
        "borderBottom": "1px solid rgba(150,188,220,0.08)",
        "padding": "12px 13px",
        "fontSize": "12px",
        "fontFamily": "Inter, system-ui, sans-serif",
        "textAlign": "left",
        "minWidth": "95px",
        "maxWidth": "220px",
        "whiteSpace": "normal",
        "height": "auto",
    },
}


app = Dash(
    __name__,
    title=APP_TITLE,
    suppress_callback_exceptions=True,
    update_title=None,
)
server = app.server


app.layout = html.Div(
    className="app-shell",
    children=[
        dcc.Interval(
            id="refresh-interval",
            interval=REFRESH_MS,
            n_intervals=0,
        ),
        html.Header(
            className="topbar",
            children=[
                html.Div(
                    className="brand",
                    children=[
                        html.Div(
                            className="brand-mark",
                            children=[
                                html.Span(),
                                html.Span(),
                                html.Span(),
                            ],
                        ),
                        html.Div(
                            children=[
                                html.Strong("GM Flood"),
                                html.Small("River Intelligence"),
                            ]
                        ),
                    ],
                ),
                html.Div(
                    className="topbar-right",
                    children=[
                        html.Span(
                            id="connection-status",
                            className="status-chip loading",
                            children="Connecting",
                        ),
                        html.Button(
                            "Refresh data",
                            id="manual-refresh",
                            className="refresh-button",
                            n_clicks=0,
                        ),
                    ],
                ),
            ],
        ),
        html.Main(
            className="dashboard-shell",
            children=[
                html.Section(
                    className="hero",
                    children=[
                        html.Div(
                            className="hero-copy",
                            children=[
                                html.Div(
                                    className="hero-intro",
                                    children=[
                                        html.Div(
                                            className="eyebrow",
                                            children=[
                                                html.Span(),
                                                "Environmental intelligence platform",
                                            ],
                                        ),
                                        html.P(
                                            className="creator-credit",
                                            children=[
                                                html.Span("Designed and modelled by"),
                                                html.Strong("Kamil Ridwan"),
                                            ],
                                        ),
                                    ],
                                ),
                                html.H1(
                                    children=[
                                        "See Greater Manchester’s rivers as a ",
                                        html.Em("living catchment."),
                                    ]
                                ),
                                html.P(
                                    "A governed public view of river levels, rainfall, flood warnings, "
                                    "monitoring stations and the data pipelines that keep each signal traceable."
                                ),
                                html.Div(
                                    className="hero-meta",
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Span("Data source"),
                                                html.Strong("Environment Agency"),
                                            ]
                                        ),
                                        html.Div(
                                            children=[
                                                html.Span("Warehouse"),
                                                html.Strong("Azure SQL"),
                                            ]
                                        ),
                                        html.Div(
                                            children=[
                                                html.Span("Last observation"),
                                                html.Strong(
                                                    "Waiting for data",
                                                    id="hero-latest-observation",
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            className="hero-orbit",
                            children=[
                                html.Div(className="orbit orbit-outer"),
                                html.Div(className="orbit orbit-middle"),
                                html.Div(className="orbit orbit-inner"),
                                html.Div(
                                    className="orbit-core",
                                    children=[
                                        html.Small("Catchment pulse"),
                                        html.Strong("—", id="hero-station-count"),
                                        html.Span("monitored stations"),
                                    ],
                                ),
                                html.Span(className="orbit-dot dot-one"),
                                html.Span(className="orbit-dot dot-two"),
                                html.Span(className="orbit-dot dot-three"),
                            ],
                        ),
                    ],
                ),
                html.Section(
                    className="technology-stack",
                    children=[
                        html.Div(
                            className="technology-copy",
                            children=[
                                html.Span("End to end engineering"),
                                html.Strong("Source to decision ready reporting"),
                                html.P(
                                    "The public experience sits on the same governed SQL reporting layer "
                                    "used by the enterprise SSRS and Power BI implementation."
                                ),
                            ],
                        ),
                        html.Div(
                            className="technology-pills",
                            children=[
                                html.Span("Environment Agency API"),
                                html.Span("Python"),
                                html.Span("SSIS"),
                                html.Span("Azure SQL"),
                                html.Span("T SQL"),
                                html.Span("SSRS"),
                                html.Span("Power BI"),
                                html.Span("Dash"),
                            ],
                        ),
                    ],
                ),
                html.Section(
                    className="metric-grid",
                    children=[
                        _metric_card(
                            "Monitored stations",
                            "metric-stations",
                            "metric-stations-detail",
                            "◉",
                            "blue",
                        ),
                        _metric_card(
                            "High river levels",
                            "metric-high-levels",
                            "metric-high-detail",
                            "↗",
                            "amber",
                        ),
                        _metric_card(
                            "Active flood warnings",
                            "metric-warnings",
                            "metric-warning-detail",
                            "!",
                            "red",
                        ),
                        _metric_card(
                            "Latest observation",
                            "metric-latest",
                            "metric-latest-detail",
                            "⌁",
                            "aqua",
                        ),
                    ],
                ),
                html.Section(
                    className="split-grid river-section",
                    children=[
                        html.Div(
                            className="panel panel-large",
                            children=[
                                _section_heading(
                                    "River intelligence",
                                    "Explore the catchment",
                                    "Select a river to inspect recent level behaviour across its monitoring stations.",
                                ),
                                html.Div(
                                    className="selector-row",
                                    children=[
                                        html.Div(
                                            className="selector-copy",
                                            children=[
                                                html.Label(
                                                    "River",
                                                    htmlFor="river-dropdown",
                                                ),
                                                html.Span(
                                                    "Live options are loaded from the governed reporting view."
                                                ),
                                            ],
                                        ),
                                        dcc.Dropdown(
                                            id="river-dropdown",
                                            options=[],
                                            value=None,
                                            placeholder="Select a river",
                                            clearable=False,
                                            className="river-dropdown",
                                        ),
                                    ],
                                ),
                                dcc.Loading(
                                    className="loading-shell",
                                    children=dcc.Graph(
                                        id="river-history-chart",
                                        figure=_empty_figure(
                                            "Choose a river to explore recent level history."
                                        ),
                                        config={
                                            "displayModeBar": False,
                                            "responsive": True,
                                        },
                                    ),
                                ),
                            ],
                        ),
                        html.Div(
                            className="panel pulse-panel",
                            children=[
                                _section_heading(
                                    "Live catchment pulse",
                                    "Selected river stations",
                                    "Latest station level, typical range and operational status.",
                                ),
                                html.Div(
                                    id="selected-river-summary",
                                    className="river-summary",
                                    children="Select a river to load station intelligence.",
                                ),
                                dash_table.DataTable(
                                    id="selected-river-table",
                                    columns=[
                                        {"name": column, "id": column}
                                        for column in [
                                            "Station",
                                            "Town",
                                            "Latest",
                                            "Unit",
                                            "Change",
                                            "Typical low",
                                            "Typical high",
                                            "Status",
                                        ]
                                    ],
                                    data=[],
                                    page_size=8,
                                    sort_action="native",
                                    **DATA_TABLE_STYLE,
                                ),
                            ],
                        ),
                    ],
                ),
                html.Section(
                    className="split-grid map-rain-grid",
                    children=[
                        html.Div(
                            className="panel",
                            children=[
                                _section_heading(
                                    "Monitoring geography",
                                    "Station network map",
                                    "Current river and rainfall monitoring locations represented in the warehouse.",
                                ),
                                dcc.Loading(
                                    children=dcc.Graph(
                                        id="station-map",
                                        figure=_empty_figure(
                                            "Station locations will appear when live data is available."
                                        ),
                                        config={
                                            "displayModeBar": False,
                                            "scrollZoom": True,
                                            "responsive": True,
                                        },
                                    )
                                ),
                            ],
                        ),
                        html.Div(
                            className="panel",
                            children=[
                                _section_heading(
                                    "Rainfall monitoring",
                                    "Latest rainfall observations",
                                    "Highest current rainfall readings across the monitored station network.",
                                ),
                                dcc.Loading(
                                    children=dcc.Graph(
                                        id="rainfall-chart",
                                        figure=_empty_figure(
                                            "Rainfall observations will appear after refresh."
                                        ),
                                        config={
                                            "displayModeBar": False,
                                            "responsive": True,
                                        },
                                    )
                                ),
                            ],
                        ),
                    ],
                ),
                html.Section(
                    className="split-grid risk-grid",
                    children=[
                        html.Div(
                            className="panel",
                            children=[
                                _section_heading(
                                    "Flood risk",
                                    "Warning summary",
                                    "Current Environment Agency warning categories represented in the reporting layer.",
                                ),
                                dcc.Loading(
                                    children=dcc.Graph(
                                        id="warning-chart",
                                        figure=_empty_figure(
                                            "Flood warning summary is loading."
                                        ),
                                        config={
                                            "displayModeBar": False,
                                            "responsive": True,
                                        },
                                    )
                                ),
                                html.Div(
                                    "Waiting for warning data",
                                    id="warning-footnote",
                                    className="panel-footnote",
                                ),
                            ],
                        ),
                        html.Div(
                            className="panel",
                            children=[
                                _section_heading(
                                    "Priority monitoring",
                                    "High river level stations",
                                    "Stations identified by the reporting logic as elevated or above their typical range.",
                                ),
                                dash_table.DataTable(
                                    id="high-level-table",
                                    columns=[
                                        {"name": column, "id": column}
                                        for column in [
                                            "Station",
                                            "River",
                                            "Town",
                                            "Level",
                                            "Typical high",
                                            "Status",
                                            "Observed",
                                        ]
                                    ],
                                    data=[],
                                    page_size=8,
                                    sort_action="native",
                                    **DATA_TABLE_STYLE,
                                ),
                            ],
                        ),
                    ],
                ),
                html.Section(
                    className="operations-section panel",
                    children=[
                        html.Div(
                            className="operations-heading",
                            children=[
                                _section_heading(
                                    "Pipeline health",
                                    "Operational trust layer",
                                    "The dashboard exposes the most recent governed ETL execution rather than hiding refresh health.",
                                ),
                                html.Div(
                                    className="etl-status-wrap",
                                    children=[
                                        html.Span(
                                            "UNKNOWN",
                                            id="etl-status",
                                            className="etl-status unknown",
                                        ),
                                        html.Span(
                                            "Waiting for pipeline history",
                                            id="etl-message",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Div(
                            className="operations-metrics",
                            children=[
                                html.Div(
                                    children=[
                                        html.Span("Last completed"),
                                        html.Strong("—", id="etl-refreshed"),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Span("Rows loaded"),
                                        html.Strong("—", id="etl-rows-loaded"),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Span("Execution duration"),
                                        html.Strong("—", id="etl-duration"),
                                    ]
                                ),
                            ],
                        ),
                    ],
                ),
                html.Section(
                    className="architecture-section",
                    children=[
                        _section_heading(
                            "Platform architecture",
                            "One governed layer, multiple consumers",
                            "The reporting views support enterprise reporting and this anonymous public portfolio experience.",
                        ),
                        html.Div(
                            className="architecture-flow",
                            children=[
                                _architecture_node(
                                    "Environment Agency",
                                    "Stations, readings, warnings",
                                ),
                                html.Span("→", className="architecture-arrow"),
                                _architecture_node(
                                    "Python ETL",
                                    "Ingestion and validation",
                                ),
                                html.Span("→", className="architecture-arrow"),
                                _architecture_node(
                                    "SSIS",
                                    "Enterprise ETL path",
                                ),
                                html.Span("→", className="architecture-arrow"),
                                _architecture_node(
                                    "Azure SQL",
                                    "Dimensional warehouse",
                                ),
                                html.Span("→", className="architecture-arrow"),
                                _architecture_node(
                                    "T SQL views",
                                    "Governed reporting layer",
                                ),
                                html.Span("→", className="architecture-arrow"),
                                _architecture_node(
                                    "SSRS · Power BI · Web",
                                    "Multiple reporting consumers",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        html.Footer(
            className="footer",
            children=[
                html.Div(
                    children=[
                        html.Strong("Greater Manchester Flood & River Intelligence"),
                        html.Span(
                            "Research and portfolio platform using publicly available Environment Agency data."
                        ),
                    ]
                ),
                html.Div(
                    className="footer-right",
                    children=[
                        html.Span("Designed and modelled by Kamil Ridwan"),
                        html.Span(
                            "This dashboard is not a replacement for official flood warning services.",
                            className="disclaimer",
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("connection-status", "children"),
    Output("connection-status", "className"),
    Output("metric-stations", "children"),
    Output("metric-stations-detail", "children"),
    Output("metric-high-levels", "children"),
    Output("metric-high-detail", "children"),
    Output("metric-warnings", "children"),
    Output("metric-warning-detail", "children"),
    Output("metric-latest", "children"),
    Output("metric-latest-detail", "children"),
    Output("hero-latest-observation", "children"),
    Output("hero-station-count", "children"),
    Output("station-map", "figure"),
    Output("rainfall-chart", "figure"),
    Output("warning-chart", "figure"),
    Output("warning-footnote", "children"),
    Output("high-level-table", "data"),
    Output("etl-status", "children"),
    Output("etl-status", "className"),
    Output("etl-message", "children"),
    Output("etl-refreshed", "children"),
    Output("etl-rows-loaded", "children"),
    Output("etl-duration", "children"),
    Output("river-dropdown", "options"),
    Output("river-dropdown", "value"),
    Input("refresh-interval", "n_intervals"),
    Input("manual-refresh", "n_clicks"),
    State("river-dropdown", "value"),
)
def refresh_dashboard(
    _interval_count: int,
    _manual_count: int,
    current_river: str | None,
):
    try:
        snapshot = load_dashboard_snapshot()
        river_names = get_river_names()

        current = snapshot["current"]
        high_levels = snapshot["high_levels"]
        rainfall = snapshot["rainfall"]
        warnings = snapshot["warnings"]
        etl = snapshot["etl"]

        station_count = (
            int(current["StationKey"].nunique())
            if not current.empty and "StationKey" in current.columns
            else 0
        )
        high_count = (
            int(high_levels["StationKey"].nunique())
            if not high_levels.empty and "StationKey" in high_levels.columns
            else len(high_levels)
        )
        active_warning_count = (
            int(pd.to_numeric(warnings["WarningCount"], errors="coerce").fillna(0).sum())
            if not warnings.empty and "WarningCount" in warnings.columns
            else 0
        )

        if not current.empty and "ReadingDateTimeUTC" in current.columns:
            latest_series = pd.to_datetime(
                current["ReadingDateTimeUTC"],
                errors="coerce",
                utc=True,
            ).dropna()
            latest_value = latest_series.max() if not latest_series.empty else None
        else:
            latest_value = None

        latest_text = _format_timestamp(latest_value)
        latest_short = (
            pd.to_datetime(latest_value, utc=True).strftime("%H:%M")
            if latest_value is not None and not pd.isna(latest_value)
            else "—"
        )

        high_detail = (
            "Stations requiring closer attention"
            if high_count
            else "No elevated stations in the current view"
        )
        warning_detail = (
            "Current warning and alert records"
            if active_warning_count
            else "No active warning records in the summary"
        )

        warning_updated = (
            _format_timestamp(
                pd.to_datetime(
                    warnings["LatestUpdateUTC"],
                    errors="coerce",
                    utc=True,
                ).max()
            )
            if not warnings.empty and "LatestUpdateUTC" in warnings.columns
            else "Not available"
        )

        etl_status, refreshed, rows_loaded, duration, etl_message = summarise_etl(etl)
        etl_class = (
            "etl-status healthy"
            if etl_status in {"SUCCEEDED", "SUCCESS", "COMPLETED"}
            else "etl-status failed"
            if etl_status in {"FAILED", "FAILURE", "ERROR"}
            else "etl-status unknown"
        )

        options = [{"label": name, "value": name} for name in river_names]
        selected = current_river if current_river in river_names else (
            river_names[0] if river_names else None
        )

        return (
            "Live data connected",
            "status-chip online",
            f"{station_count:,}",
            "Unique stations in the current reporting view",
            f"{high_count:,}",
            high_detail,
            f"{active_warning_count:,}",
            warning_detail,
            latest_short,
            latest_text,
            latest_text,
            f"{station_count:,}",
            build_station_map(current),
            build_rainfall_chart(rainfall),
            build_warning_chart(warnings),
            f"Latest warning update: {warning_updated}",
            build_high_level_table(high_levels),
            etl_status,
            etl_class,
            etl_message,
            refreshed,
            rows_loaded,
            duration,
            options,
            selected,
        )

    except Exception as exc:
        message = str(exc)
        empty_map = _empty_figure(
            "Live station data is temporarily unavailable. The platform will retry automatically."
        )
        empty_rain = _empty_figure(
            "Rainfall data is temporarily unavailable."
        )
        empty_warning = _empty_figure(
            "Flood warning data is temporarily unavailable."
        )

        return (
            "Data connection unavailable",
            "status-chip offline",
            "—",
            "Waiting for Azure SQL",
            "—",
            "Waiting for Azure SQL",
            "—",
            "Waiting for Azure SQL",
            "—",
            "Waiting for live observations",
            "Waiting for live data",
            "—",
            empty_map,
            empty_rain,
            empty_warning,
            "The dashboard will retry automatically.",
            [],
            "UNAVAILABLE",
            "etl-status failed",
            message,
            "—",
            "—",
            "—",
            [],
            None,
        )


@app.callback(
    Output("river-history-chart", "figure"),
    Output("selected-river-table", "data"),
    Output("selected-river-summary", "children"),
    Input("river-dropdown", "value"),
)
def refresh_selected_river(river_name: str | None):
    if not river_name:
        return (
            _empty_figure("Choose a river to explore recent level history."),
            [],
            "Select a river to load station intelligence.",
        )

    try:
        history = get_river_history(river_name)
        stations = get_current_river_stations(river_name)

        station_count = len(stations)
        elevated_count = 0

        if not stations.empty and "CurrentStatus" in stations.columns:
            status = stations["CurrentStatus"].fillna("").astype(str).str.upper()
            elevated_count = int(
                status.str.contains("ABOVE|ELEVATED", regex=True).sum()
            )

        summary = (
            f"{station_count:,} station"
            f"{'s' if station_count != 1 else ''} represented, "
            f"{elevated_count:,} currently elevated or above typical range."
        )

        return (
            build_river_history_chart(river_name, history),
            build_station_table(stations),
            summary,
        )

    except Exception as exc:
        return (
            _empty_figure(
                f"{river_name} data could not be loaded. The platform will retry on the next refresh."
            ),
            [],
            str(exc),
        )


if __name__ == "__main__":
    port = int(
        os.getenv(
            "PORT",
            "8050",
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )
