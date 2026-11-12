"""Tests for all eight routes, validation, and independent gearing examples."""

import unittest
from copy import deepcopy
from math import pi
from drafter import Page
import main


class ShiftPointTests(unittest.TestCase):
    """Use fresh State instances so tests cannot affect one another."""

    def setUp(self) -> None:
        """Create a fresh setup before every test."""
        self.state = main.initial_state()

    def test_index(self) -> None:
        """Home exposes the setup button."""
        page = main.index(self.state)
        self.assertIsInstance(page, Page)
        self.assertIn("Start setup", str(page))

    def test_vehicle_setup(self) -> None:
        """Vehicle page contains both labeled form fields."""
        page = main.vehicle_setup(self.state)
        self.assertIn("final_drive", str(page))
        self.assertIn("tire_diameter_in", str(page))

    def test_gear_setup(self) -> None:
        """Gear page exposes all five input names."""
        page = main.gear_setup(self.state)
        for number in range(1, 6):
            self.assertIn("gear" + str(number), str(page))

    def test_targets(self) -> None:
        """Targets page contains both calculation inputs."""
        page = main.targets(self.state)
        self.assertIn("engine_rpm", str(page))
        self.assertIn("target_mph", str(page))

    def test_save_vehicle(self) -> None:
        """Valid setup changes both fields and opens the gear page."""
        page = main.save_vehicle(self.state, "4.1", "28")
        self.assertEqual(self.state.final_drive, 4.1)
        self.assertEqual(self.state.tire_diameter_in, 28)
        self.assertIn("Transmission gears", str(page))

    def test_save_gears(self) -> None:
        """Saving gears meaningfully replaces the dataclass list."""
        page = main.save_gears(self.state, "4", "3", "2", "1", "0.6")
        self.assertEqual(self.state.gears, [
            main.Gear(1, 4), main.Gear(2, 3), main.Gear(3, 2),
            main.Gear(4, 1), main.Gear(5, 0.6),
        ])
        self.assertIn("Choose your calculation", str(page))

    def test_calculate(self) -> None:
        """Valid calculation updates both target fields and displays results."""
        page = main.calculate(self.state, "4000", "70")
        self.assertEqual(self.state.engine_rpm, 4000)
        self.assertEqual(self.state.target_mph, 70)
        self.assertIn("Your gearing results", str(page))

    def test_results(self) -> None:
        """The sample setup produces five rows with independently checked data."""
        page = main.results(self.state)
        table = page.content[2]
        self.assertEqual(len(table.rows), 5)
        self.assertEqual(table.rows[0], ["1", "3.0", "22.1", "8145"])
        self.assertEqual(table.rows[4], ["5", "0.75", "88.4", "2036"])

    def test_vehicle_errors_do_not_save(self) -> None:
        """Invalid numbers and out-of-range entries leave setup intact."""
        for drive, diameter in [("", "26"), ("nan", "26"), ("inf", "26"),
                                ("0", "26"), ("21", "26"), ("4", "0"),
                                ("4", "101"), ("4", "abc")]:
            old = deepcopy(self.state)
            page = main.save_vehicle(self.state, drive, diameter)
            self.assertEqual(self.state.final_drive, old.final_drive)
            self.assertEqual(self.state.tire_diameter_in, old.tire_diameter_in)
            self.assertIn("Vehicle setup", str(page))
            self.assertNotEqual(self.state.message, "")

    def test_gear_errors_do_not_save(self) -> None:
        """Failure at the last gear does not partially save earlier gear edits."""
        old_gears = deepcopy(self.state.gears)
        page = main.save_gears(self.state, "5", "4", "3", "2", "oops")
        self.assertEqual(self.state.gears, old_gears)
        self.assertIn("gear 5", str(page))

    def test_target_errors_do_not_save(self) -> None:
        """Reject invalid targets and preserve both prior accepted values."""
        for rpm, mph in [("-1", "60"), ("20001", "60"), ("abc", "60"),
                         ("4000", "-1"), ("4000", "501"), ("4000", "nan")]:
            main.calculate(self.state, rpm, mph)
            self.assertEqual(self.state.engine_rpm, 3000)
            self.assertEqual(self.state.target_mph, 60)

    def test_zero_targets(self) -> None:
        """Zero targets are supported by the numerical solver."""
        page = main.calculate(self.state, "0", "0")
        for row in page.content[2].rows:
            self.assertEqual(row[2:], ["0.0", "0"])

    def test_hand_example(self) -> None:
        """At 1:1 gearing a 1056-inch circumference gives 60 mph at 60 RPM."""
        diameter = 1056 / pi
        self.assertAlmostEqual(main.speed_mph(60, 1, 1, diameter), 60)
        self.assertAlmostEqual(main.rpm_at_speed(60, 1, 1, diameter), 60)

    def test_numpy_matches_scalar_math(self) -> None:
        """Array results agree with scalar wheel-circumference calculations."""
        speeds = main.speeds_for_gears(self.state)
        for gear, actual in zip(self.state.gears, speeds):
            expected = 3000 / (gear.ratio * 3.5) * (pi * 26) / 1056
            self.assertAlmostEqual(actual, expected)

    def test_round_trip_and_edit(self) -> None:
        """Changing the setup updates results and inverse calculations."""
        before = main.speeds_for_gears(self.state)[0]
        main.save_vehicle(self.state, "7", "26")
        after = main.speeds_for_gears(self.state)[0]
        self.assertAlmostEqual(after, before / 2)
        self.assertAlmostEqual(main.rpm_at_speed(after, 3, 7, 26), 3000)

    def test_read_number(self) -> None:
        """Parse whitespace and decimals, rejecting malformed or infinite input."""
        self.assertEqual(main.read_number(" 3.5 "), 3.5)
        for text in ["", "abc", "NaN", "Infinity", "1e999"]:
            self.assertEqual(main.read_number(text), -1)

    def test_initial_state_is_independent(self) -> None:
        """Creating a new setup does not share mutable gears with another."""
        other = main.initial_state()
        self.state.gears[0].ratio = 9
        self.assertEqual(other.gears[0].ratio, 3)


if __name__ == "__main__":
    unittest.main()
