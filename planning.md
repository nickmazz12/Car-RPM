# ShiftPoint implementation plan
Nicholas Mazzella — CISC106

This plan records the implemented design. Upload the original completed selection
and design worksheets alongside it for the course's repository requirement.

## Purpose
Help students understand how a vehicle's gears, final drive, tire diameter,
engine RPM, and road speed relate. Use one five-speed setup.

## Page flow
Home (index) -> Vehicle Setup (vehicle_setup) -> Gear Setup (gear_setup)
-> Calculation Targets (targets) -> Results (results).
Start setup opens vehicle_setup. Continue submits to save_vehicle.
Save gears submits to save_gears. Calculate submits to calculate.
Results links back to the three input pages and Home.
Invalid submissions return to the relevant form with an explanation.

## State
| Field | Type | Modified in |
|---|---|---|
| final_drive | float | save_vehicle |
| tire_diameter_in | float | save_vehicle |
| gears | list[Gear] | save_gears |
| engine_rpm | float | calculate |
| target_mph | float | calculate |
| message | str | the three submission routes |

Gear has number: int and ratio: float. Valid gear submissions build and save a new
list of five Gear instances. Results loops over state.gears to produce table rows.

## Rubric map
- 8 routes, 5 distinct pages
- 6 State fields, with all 6 meaningfully modified by submission routes
- Gear as a second dataclass and state.gears as a list of Gear instances
- 9 TextBox inputs
- Meaningful conditionals validate final drive, diameter, ratios, RPM, and speed
- Results iterates over state.gears and uses gear.number and gear.ratio
- Drafter provides all pages, routes, input components, buttons, and the table
- No mutable global application variables
- All function headers have annotations and every function has a docstring
- Advanced techniques documented near use
- Tests cover all eight routes and calculation helpers
- main.py calls set_site_information

## Implementation decisions
The initial data is an example rather than a particular car's specification.
Input ranges prevent impractical and numerically extreme calculations.
Valid data is committed only after every field on a form passes validation.
NumPy computes speeds across the gear array. SciPy solves the inverse speed
equation with brentq. The direct inverse formula would also work, but using the
solver provides numerical-method practice.

## Remaining submission checks
Deploy to a public GitHub repository and test the actual public URL.
Record all pages and outcome groups with audible narration and a visible address
bar in under five minutes. Add a public video link to README.md.
Include the original selection/design worksheets and a full AI transcript.
