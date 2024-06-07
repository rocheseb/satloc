import argparse
from skyfield.api import load, wgs84
from skyfield.sgp4lib import EarthSatellite
from skyfield.timelib import Timescale
from datetime import datetime, UTC, timedelta
import pytz
from timezonefinder import TimezoneFinder
import geoviews as gv
import holoviews as hv

hv.extension("bokeh")


def satellite_coordinates(
    satellite: EarthSatellite, timescale: Timescale, when: datetime = datetime.now(UTC)
) -> tuple[float, float]:

    t = timescale.utc(*when.timetuple()[:6])

    latitude, longitude = [i.degrees for i in wgs84.latlon_of(satellite.at(t))]

    return latitude, longitude


def satellite_track(
    norad_catalog_number: int | str, when: datetime = datetime.now(UTC), forecast_hours: float = 1.5
):
    celestrak_url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_catalog_number}"
    satellite = load.tle_file(celestrak_url, reload=True)[0]
    timescale = load.timescale()

    # number of 30 sec intervals = hours_forcast * 3600 / 30
    n_interval = int(forecast_hours * 120)

    times = [when + timedelta(seconds=30 * i) for i in range(n_interval)]

    latitudes, longitudes = zip(
        *[satellite_coordinates(satellite, timescale, when=i) for i in times]
    )

    return times, latitudes, longitudes


def split_orbit_track(longitudes, latitudes):
    """
    Splits the satellite orbit path into segments to handle crossings at the 180/-180 longitude.
    Returns a list of dictionaries where each dictionary represents a segment with "Longitude" and "Latitude" keys.
    """
    segments = []
    current_segment = {"Longitude": [], "Latitude": []}

    for i in range(len(longitudes)):
        if (
            current_segment["Longitude"]
            and abs(longitudes[i] - current_segment["Longitude"][-1]) > 180
        ):
            # Split the segment if there is a crossing
            segments.append(current_segment)
            current_segment = {"Longitude": [], "Latitude": []}

        current_segment["Longitude"].append(longitudes[i])
        current_segment["Latitude"].append(latitudes[i])

    # Add the last segment
    if current_segment["Longitude"]:
        segments.append(current_segment)

    return segments


def make_map(times, latitudes, longitudes, title: str = ""):

    tf = TimezoneFinder()

    local_timezones = [
        tf.timezone_at(lng=longitudes[i], lat=latitudes[i]) for i, v in enumerate(times)
    ]

    data = {
        "Longitude": longitudes,
        "Latitude": latitudes,
        "UTC Time": [datetime.strftime(i, "%Y-%m-%d %H:%M:%S") for i in times],
        "Local Time": [
            datetime.strftime(
                v.astimezone(pytz.timezone(local_timezones[i])),
                "%Y-%m-%d %H:%M:%S",
            )
            + f" ({local_timezones[i]})"
            for i, v in enumerate(times)
        ],
    }

    for tz_str in ["America/New_York", "Pacific/Auckland", "Europe/Paris"]:
        data[tz_str] = [
            datetime.strftime(
                v.astimezone(pytz.timezone(tz_str)),
                "%Y-%m-%d %H:%M:%S",
            )
            for i, v in enumerate(times)
        ]

    vdims = ["Longitude", "Latitude"]

    initial_position = gv.Points([(longitudes[0], latitudes[0])], vdims=vdims)

    markers_30sec = gv.Points(
        data,
        vdims,
        [
            "Longitude",
            "Latitude",
            "UTC Time",
            "Local Time",
            "America/New_York",
            "Pacific/Auckland",
            "Europe/Paris",
        ],
    )

    data_10min = {k: [val for i, val in enumerate(v) if i % 20 == 0] for k, v in data.items()}

    markers_10min = gv.Points(data_10min, vdims)

    orbit_track_segments = split_orbit_track(longitudes, latitudes)

    orbit_tracks = [gv.Path(i, vdims=vdims) for i in orbit_track_segments]

    map_plot = gv.tile_sources.EsriWorldStreetMap.opts(
        width=800,
        height=700,
        active_tools=["pan", "wheel_zoom"],
        title=title,
    )

    for i in orbit_tracks:
        map_plot *= i.opts(color="blue", line_width=2)

    map_plot *= (
        markers_30sec.opts(color="green", size=4, tools=["hover"])
        * markers_10min.opts(color="orange", size=5)
        * initial_position.opts(color="red", size=8)
    )

    forecast_hours = (times[-1] - times[0]).total_seconds() / 3600

    div_text = f"""
    Hover over markers to see coordinates.<br>
    <br>
    The track starts at the red marker at {data["UTC Time"][0]} (UTC). <br>
    Green markers predict the satellite position in 30 second intervals for {forecast_hours:.1f} hours<br>
    Orange markers are in 10 min intervals.
    """

    div = hv.Div(div_text).opts(width=200, height=300)

    map_plot = div + map_plot

    return map_plot


def plot_satellite_tracks(
    norad_catalog_number: int | str,
    out_path: str = "satellite_track.",
    when: datetime = datetime.now(UTC),
    forecast_hours: float = 1.5,
    title: str = "",
) -> None:
    times, latitudes, longitudes = satellite_track(
        norad_catalog_number, when=when, forecast_hours=forecast_hours
    )

    map_plot = make_map(times, latitudes, longitudes, title=title)

    hv.save(map_plot, out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("norad_catalog_number", type=int, help="NORAD catalog number")
    parser.add_argument(
        "-d",
        "--date",
        default=None,
        help="time at which the satellite position will computed in YYYYMMDDTHHMMSS format, defaults to now",
    )
    parser.add_argument(
        "-o", "--out-path", default="satellite_track.html", help="full path to the output html plot"
    )
    parser.add_argument("-t", "--title", default="", help="plot title")
    parser.add_argument(
        "-f",
        "--forecast-hours",
        type=float,
        default=1.5,
        help="How far after --date the track will be calculated (in hours)",
    )
    args = parser.parse_args()

    if args.date is None:
        args.date = datetime.now(UTC)
    else:
        args.date = datetime.strptime(args.date, "%Y%M%DT%H%M%S")

    plot_satellite_tracks(
        args.norad_catalog_number, args.out_path, args.date, args.forecast_hours, args.title
    )


if __name__ == "__main__":
    main()
