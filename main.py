"""ShiftPoint: a five-speed vehicle gearing calculator.

Advanced techniques are explained near their use.
NumPy calculates speeds for multiple gears.
SciPy numerically solves for RPM at a target speed.
"""

from drafter.components.page_content import Component
from dataclasses import dataclass
from math import isfinite, pi

import numpy as np
f# The deployment type checker lacks SciPy's optional type stubs.
from scipy.optimize import brentq  # type: ignore[import-untyped]

from drafter import (
    Page,
    Header,
    Paragraph,
    TextBox,
    Label,
    Button,
    Table,
    route,
    start_server,
    set_site_information,
    add_website_css,
)


INCHES_PER_MILE = 63360
MINUTES_PER_HOUR = 60


@dataclass
class Gear:
    """Represent one transmission gear and its ratio."""

    number: int
    ratio: float


@dataclass
class State:
    """Store the current vehicle setup and calculation inputs."""

    final_drive: float
    tire_diameter_in: float
    gears: list[Gear]
    engine_rpm: float
    target_mph: float
    message: str


def initial_state() -> State:
    """Create a fresh example vehicle setup."""
    return State(
        3.5,
        26.0,
        [
            Gear(1, 3.0),
            Gear(2, 2.0),
            Gear(3, 1.5),
            Gear(4, 1.0),
            Gear(5, 0.75),
        ],
        3000.0,
        60.0,
        "",
    )


def read_number(text: str) -> float:
    """Convert input to a finite number or return -1 for invalid input.

    Advanced technique: try/except handles invalid text without
    crashing the program. isfinite rejects infinity and NaN.
    """
    try:
        number = float(text)
    except (ValueError, TypeError):
        return -1.0

    if not isfinite(number):
        return -1.0

    return number


def speed_mph(
    rpm: float,
    ratio: float,
    final_drive: float,
    diameter: float,
) -> float:
    """Calculate mph from RPM, gearing, and tire diameter in inches."""
    wheel_rpm = rpm / (ratio * final_drive)
    inches_per_minute = wheel_rpm * pi * diameter

    return inches_per_minute * MINUTES_PER_HOUR / INCHES_PER_MILE


def speeds_for_gears(state: State) -> list[float]:
    """Calculate road speed for each gear using NumPy.

    Advanced technique: a NumPy array applies arithmetic to every
    gear ratio at once. tolist converts the results to a Python list.
    """
    ratios = []

    for gear in state.gears:
        ratios.append(gear.ratio)

    ratio_array = np.array(ratios, dtype=float)

    speeds = (
        state.engine_rpm
        * pi
        * state.tire_diameter_in
        * MINUTES_PER_HOUR
        / (ratio_array * state.final_drive * INCHES_PER_MILE)
    )

    return speeds.tolist()


def speed_error(
    rpm: float,
    ratio: float,
    final_drive: float,
    diameter: float,
    target: float,
) -> float:
    """Find the difference between calculated and requested speed."""
    return speed_mph(rpm, ratio, final_drive, diameter) - target


def rpm_at_speed(
    target: float,
    ratio: float,
    final_drive: float,
    diameter: float,
) -> float:
    """Use SciPy to find the RPM needed for a target speed.

    Advanced technique: brentq finds where speed_error equals zero.
    The args tuple supplies the additional function arguments.

    The upper bound is twice the direct-formula result plus one,
    ensuring the solution is inside the search interval.

    A direct formula could also solve this problem. Using SciPy
    provides practice with numerical methods.
    """
    upper = (
        2 * target * ratio * final_drive * INCHES_PER_MILE
        / (pi * diameter * MINUTES_PER_HOUR)
        + 1
    )

    return float(
        brentq(
            speed_error,
            0.0,
            upper,
            args=(ratio, final_drive, diameter, target),
        )
    )


@route
def index(state: State) -> Page:
    """Display the homepage and explain the calculator."""
    return Page(
        state,
        [
            Header("ShiftPoint"),
            Paragraph(
                "Explore the connection between engine RPM "
                "and road speed."
            ),
            Paragraph(
                "Enter one vehicle setup and calculate results "
                "for five forward gears."
            ),
            Paragraph(
                "The starting values are an example setup. "
                "Enter your own vehicle specifications."
            ),
            Paragraph(
                "This model assumes an engaged clutch and no tire "
                "slip. Available power and engine limits determine "
                "which calculated speeds a real car can reach."
            ),
            Button("Start setup", vehicle_setup),
        ],
    )


@route
def vehicle_setup(state: State) -> Page:
    """Display inputs for final-drive ratio and tire diameter."""
    return Page(
        state,
        [
            Header("1 / Vehicle setup"),
            Paragraph(state.message),
            Label(
                "Final-drive ratio (0.1 to 20)",
                "final_drive",
            ),
            TextBox("final_drive", str(state.final_drive)),
            Label(
                "Tire diameter in inches (5 to 100)",
                "tire_diameter_in",
            ),
            TextBox(
                "tire_diameter_in",
                str(state.tire_diameter_in),
            ),
            Button("Continue", save_vehicle),
            Button("Home", index),
        ],
    )


@route
def save_vehicle(
    state: State,
    final_drive: str,
    tire_diameter_in: str,
) -> Page:
    """Validate and save both vehicle setup inputs."""
    drive = read_number(final_drive)
    diameter = read_number(tire_diameter_in)

    if drive < 0.1 or drive > 20:
        state.message = (
            "Enter a final-drive ratio from 0.1 to 20."
        )
        return vehicle_setup(state)

    if diameter < 5 or diameter > 100:
        state.message = (
            "Enter a tire diameter from 5 to 100 inches."
        )
        return vehicle_setup(state)

    state.final_drive = drive
    state.tire_diameter_in = diameter
    state.message = ""

    return gear_setup(state)


@route
def gear_setup(state: State) -> Page:
    """Display five transmission gear-ratio inputs."""
    return Page(
        state,
        [
            Header("2 / Transmission gears"),
            Paragraph(state.message),
            Paragraph(
                "Enter each forward gear ratio from 0.1 to 20."
            ),
            Label("First gear", "gear1"),
            TextBox("gear1", str(state.gears[0].ratio)),
            Label("Second gear", "gear2"),
            TextBox("gear2", str(state.gears[1].ratio)),
            Label("Third gear", "gear3"),
            TextBox("gear3", str(state.gears[2].ratio)),
            Label("Fourth gear", "gear4"),
            TextBox("gear4", str(state.gears[3].ratio)),
            Label("Fifth gear", "gear5"),
            TextBox("gear5", str(state.gears[4].ratio)),
            Button("Save gears", save_gears),
            Button("Back to vehicle", vehicle_setup),
        ],
    )


@route
def save_gears(
    state: State,
    gear1: str,
    gear2: str,
    gear3: str,
    gear4: str,
    gear5: str,
) -> Page:
    """Validate all gear ratios before replacing the stored list."""
    new_gears = []
    number = 1

    for entry in [gear1, gear2, gear3, gear4, gear5]:
        ratio = read_number(entry)

        if ratio < 0.1 or ratio > 20:
            state.message = (
                "Enter a ratio from 0.1 to 20 for gear "
                + str(number)
                + "."
            )
            return gear_setup(state)

        new_gears.append(Gear(number, ratio))
        number += 1

    state.gears = new_gears
    state.message = ""

    return targets(state)


@route
def targets(state: State) -> Page:
    """Display engine RPM and target road-speed inputs."""
    return Page(
        state,
        [
            Header("3 / Choose your calculation"),
            Paragraph(state.message),
            Label(
                "Engine RPM (0 to 20000)",
                "engine_rpm",
            ),
            TextBox("engine_rpm", str(state.engine_rpm)),
            Label(
                "Target speed in mph (0 to 500)",
                "target_mph",
            ),
            TextBox("target_mph", str(state.target_mph)),
            Button("Calculate", calculate),
            Button("Back to gears", gear_setup),
        ],
    )


@route
def calculate(
    state: State,
    engine_rpm: str,
    target_mph: str,
) -> Page:
    """Validate calculation inputs and open the results page."""
    rpm = read_number(engine_rpm)
    speed = read_number(target_mph)

    if rpm < 0 or rpm > 20000:
        state.message = "Enter engine RPM from 0 to 20000."
        return targets(state)

    if speed < 0 or speed > 500:
        state.message = "Enter target speed from 0 to 500 mph."
        return targets(state)

    state.engine_rpm = rpm
    state.target_mph = speed
    state.message = ""

    return results(state)


@route
def results(state: State) -> Page:
    """Build a results table by looping over the stored Gear objects."""
    speeds = speeds_for_gears(state)
    rows: list[list[Component | str | int | float | bool]] = []

    for gear in state.gears:
        rpm = rpm_at_speed(
            state.target_mph,
            gear.ratio,
            state.final_drive,
            state.tire_diameter_in,
        )

        rows.append(
            [
                str(gear.number),
                str(gear.ratio),
                str(round(speeds[gear.number - 1], 1)),
                str(round(rpm)),
            ]
        )

    return Page(
        state,
        [
            Header("4 / Your gearing results"),
            Paragraph(
                "Final drive "
                + str(state.final_drive)
                + " | Tire diameter "
                + str(state.tire_diameter_in)
                + " inches"
            ),
            Table(
                rows,
                [
                    "Gear",
                    "Ratio",
                    "mph at "
                    + str(state.engine_rpm)
                    + " RPM",
                    "RPM at "
                    + str(state.target_mph)
                    + " mph",
                ],
            ),
            Paragraph(
                "A larger numerical gear ratio gives less road "
                "speed at the same RPM. A larger tire diameter "
                "gives more road speed at the same RPM."
            ),
            Paragraph(
                "Calculated RPM may exceed your engine's operating "
                "range. Use the table to explore gearing relationships."
            ),
            Button("Edit targets", targets),
            Button("Edit gears", gear_setup),
            Button("Edit vehicle", vehicle_setup),
            Button("Home", index),
        ],
    )


set_site_information(
    author="Nicholas Mazzella",
    description=(
        "ShiftPoint explores speed and engine RPM "
        "across five forward gears."
    ),
    sources=[
        "https://drafter-edu.github.io/drafter/",
        "https://numpy.org/doc/stable/",
        (
            "https://docs.scipy.org/doc/scipy/reference/"
            "generated/scipy.optimize.brentq.html"
        ),
        "https://tremec.com/aftermarket/resources/gear-ratio-calculator/",
    ],
    planning=["planning.md"],
    links=["README.md"],
)


# Advanced technique: CSS changes the site's visual appearance.
# It controls colors, spacing, input borders, buttons, and table cells.
add_website_css("""
body {
    background: #eef2f5;
    color: #182c3d;
    font-family: Arial, sans-serif;
}

h1 {
    color: #102e43;
    letter-spacing: -0.035em;
}

label {
    display: block;
    margin-top: 16px;
    font-weight: bold;
}

input {
    padding: 10px;
    border: 1px solid #a4b5c2;
    border-radius: 6px;
}

button {
    padding: 12px 18px;
    margin: 12px 8px 8px 0;
    border-radius: 6px;
    background: #136c65;
    color: white;
    border: none;
    cursor: pointer;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}

td, th {
    padding: 12px;
    border-bottom: 1px solid #becbd3;
    text-align: left;
}
""")


# Advanced technique: the main guard starts the website when this
# file runs directly and allows test_main.py to import its functions.
if __name__ == "__main__":
    start_server(
        initial_state(),
        engine="pyodide",
        site_title="ShiftPoint",
        project_packages=["numpy", "scipy"],
    )
