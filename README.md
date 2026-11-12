# ShiftPoint
A Drafter project by Nicholas Mazzella for CISC106.

Explore speed and engine RPM for one five-speed vehicle. The starting values
are examples. Enter your own gear ratios, final-drive ratio, and tire diameter.

## Current status
The Python tests pass and Drafter compilation succeeds. GitHub deployment,
live browser verification, the public narrated video, and the complete AI
transcript still need to be completed. There is no deployed URL yet.

## Run in Thonny
Install the packages listed in requirements.txt using Tools > Manage packages.
Open main.py and press Run. Use the Python interpreter in which those packages
were installed. Internet access is needed to load the browser Python runtime.
The program selects Pyodide for NumPy and SciPy support.

## Run from a terminal
    python -m pip install -r requirements.txt
    python -m unittest -v
    python main.py

## GitHub Pages deployment
1. Create a public repository named shiftpoint on your GitHub account.
2. Upload the contents of this project folder to the repository root.
   Include .github/workflows/deploy.yml. If your upload method skips hidden
   folders, create that exact file through GitHub's Add file > Create new file.
3. Use a descriptive commit message such as "Build five-gear RPM calculator".
4. Under Settings > Pages, choose GitHub Actions as the source.
5. Under Actions, open Test and deploy ShiftPoint and run the workflow.
6. Open the website URL shown by the successful deployment job.
7. Click through every page, test invalid entries and changed values, and check
   on a phone. Confirm that the repository is Public.
8. Add the actual deployed URL to this README.
9. Record the public website with your address bar visible and your voice audible.
10. Upload the video, enable public viewing, test its link while signed out,
    and replace the pending video text below with its working link.

This workflow tests and deploys on pushes to main and also supports manual runs.
Keep the working source in main.py. The workflow regenerates dist automatically.

Official deployment guide
https://drafter-edu.github.io/drafter/your-project/deploy/github-pages/

## Demonstration video
PENDING — add the publicly accessible recording link here before submission.
Use video_script.md to cover all pages, outcomes, and requirements within five minutes.

## Required course documents
- planning.md is an implementation plan based on the decisions in this chat.
- Upload your actual submitted selection and design worksheets too.
- Upload the complete project-related AI conversation, including code and future
  changes. See AI_CONVERSATION_REQUIRED.md. That notice is not a transcript.

## Verification
17 Python unit tests cover every route and calculation helpers, successful saves,
rejected inputs, unchanged state on invalid forms, zero values, and edited setups.
Compilation passed with Drafter 2.2.0. Interactive local and public browser testing
remain pending because the available browser could not access the local server.

## Model and units
Road speed = engine RPM / (gear ratio * final drive) * pi * tire diameter / 1056.
Tire diameter is in inches and speed is in mph. The constant 1056 equals
63,360 inches per mile divided by 60 minutes per hour.
The model assumes no tire slip and a fully engaged clutch.
Required RPM can exceed the engine's operating range.

## Code map
main.py contains all application code, dataclasses, and eight routes.
test_main.py contains unit tests.
NumPy array arithmetic, SciPy root finding, try/except, CSS, and the main guard
are explained in comments and docstrings.
