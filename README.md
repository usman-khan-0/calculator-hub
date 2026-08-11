# Calculator Hub

A modern, offline, all-in-one Android calculator app built with **Python**, **Kivy**, and **KivyMD**.

Calculator Hub bundles eleven calculator types into one polished, Material-Design mobile app:

1. Simple Calculator
2. 991ES-style Scientific Calculator
3. GPA Calculator
4. CGPA Calculator
5. Semester GPA Calculator
6. Cumulative GPA Calculator
7. Percentage Calculator
8. Grade Calculator
9. Average Calculator
10. Basic Math Calculator
11. Unit Converter

The app requires **no internet connection**. Calculation history and settings are stored locally in SQLite.

---

## 1. Project structure

```
calculator_hub/
│
├── main.py                     # App entry point (ScreenManager, theming, storage wiring)
├── requirements.txt
├── buildozer.spec
├── README.md
│
├── app/
│   ├── screens/                # UI screens (thin — delegate to calculators/)
│   │   ├── home_screen.py
│   │   ├── calculator_screen.py    # Simple/Scientific/GPA/CGPA/%/Grade/Average/Unit screens
│   │   ├── settings_screen.py
│   │   └── history_screen.py
│   │
│   ├── calculators/             # Pure-Python calculation engines (no Kivy import)
│   │   ├── basic.py
│   │   ├── scientific.py
│   │   ├── gpa.py
│   │   ├── cgpa.py
│   │   ├── percentage.py
│   │   ├── grade.py
│   │   ├── average.py
│   │   └── unit_converter.py
│   │
│   ├── components/               # Reusable KivyMD widgets
│   │   ├── calculator_button.py
│   │   ├── calculator_card.py
│   │   └── input_field.py
│   │
│   ├── utils/
│   │   ├── calculations.py       # Safe AST-based expression evaluator (no eval())
│   │   ├── validators.py         # Input validation helpers
│   │   └── storage.py            # SQLite history + settings
│   │
│   └── data/
│       └── grade_scales.py       # Configurable GPA scales & grade boundary tables
│
├── assets/
│   ├── icons/                    # Put your own app icon here (see buildozer.spec)
│   └── images/                   # Put your own presplash image here
│
├── kv/
│   ├── home.kv
│   ├── calculator.kv
│   ├── settings.kv
│   └── history.kv
│
└── tests/                        # Unit tests for every calculation engine
    ├── test_calculations.py
    ├── test_gpa.py
    ├── test_cgpa.py
    ├── test_percentage.py
    ├── test_grade.py
    ├── test_average.py
    └── test_unit_converter.py
```

**Architecture note:** every calculator's math lives in `app/calculators/*.py` as plain
Python classes/functions with **zero Kivy imports**. Screens in `app/screens/` only read
widget state, call the engine, and render the result. This is what makes the engines
independently unit-testable and makes it easy to add a 12th, 13th, ... calculator later —
just add a new module in `calculators/`, a screen class, a `kv` rule, and one entry in
`CALCULATOR_REGISTRY` inside `app/screens/home_screen.py`.

---

## 2. Installing dependencies

Requires **Python 3.9+**.

```bash
cd calculator_hub
python3 -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

> Kivy has some platform-specific build prerequisites (SDL2, GStreamer, etc.).
> If `pip install kivy` fails, follow the official platform guide first:
> https://kivy.org/doc/stable/gettingstarted/installation.html

---

## 3. Running the application locally

```bash
python3 main.py
```

This launches Calculator Hub in a desktop window using Kivy's SDL2 backend — the same
UI and navigation you'll get on Android, just running on your computer. On a headless
Linux machine (e.g. CI, containers, remote servers) run it under a virtual display:

```bash
xvfb-run -a python3 main.py
```

Local runs store the SQLite database and history at the current working directory
(`user_data_dir`); on Android it lives in the app's private storage automatically.

---

## 4. Running the tests

All calculation engines are covered by unit tests that do **not** require Kivy to be
importable — they test `app/calculators/*.py` directly.

```bash
python3 -m pytest tests/ -v
```

64 tests currently cover: arithmetic, parentheses, division-by-zero, unsafe-input
rejection, trig functions in both DEG/RAD modes, logs, powers, factorials, GPA/CGPA
across multiple grading scales, percentage operations, grade boundaries, average/median/
mode, and every unit-conversion category.

---

## 5. Installing Buildozer

Buildozer automates the Android SDK/NDK setup and packaging. On Linux/macOS:

```bash
pip install buildozer cython
```

You'll also need the Android build prerequisites (Java JDK 17, `unzip`, `autoconf`,
`libtool`, etc.). See the official guide for your OS:
https://buildozer.readthedocs.io/en/latest/installation.html

> Buildozer on Windows is not officially supported — use WSL2 (Windows Subsystem for
> Linux) instead.

---

## 6. Building a debug APK

From the project root (where `buildozer.spec` lives):

```bash
buildozer -v android debug
```

The first run downloads the Android SDK/NDK (several GB) and will take a while. The
resulting APK is written to `./bin/calculatorhub-1.0.0-arm64-v8a_armeabi-v7a-debug.apk`.

---

## 7. Building an Android release / AAB

1. Generate a signing keystore (once):

   ```bash
   keytool -genkey -v -keystore calculatorhub-release.keystore \
       -alias calculatorhub -keyalg RSA -keysize 2048 -validity 10000
   ```

2. Build the release artifact (an `.aab`, per `android.release_artifact` in
   `buildozer.spec`):

   ```bash
   buildozer -v android release
   ```

3. Sign and align it (or point `buildozer.spec`'s `[app]` keystore settings at your
   keystore and let Buildozer sign automatically):

   ```bash
   jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
       -keystore calculatorhub-release.keystore \
       ./bin/calculatorhub-1.0.0-arm64-v8a_armeabi-v7a-release.aab calculatorhub
   ```

4. Upload the signed `.aab` to the Google Play Console.

---

## 8. Installing the APK on an Android phone

**Option A — USB + adb:**

```bash
adb install ./bin/calculatorhub-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

**Option B — direct transfer:** copy the `.apk` file to your phone (e.g. via USB, email,
or cloud storage), open it from a file manager, and allow "install from unknown sources"
when prompted.

**Live-reload while developing:** `buildozer android debug deploy run logcat` will
install, launch, and stream logs from a connected device in one step.

---

## 9. Key dependencies

| Dependency | Purpose |
|---|---|
| `Kivy` | Cross-platform UI toolkit / rendering engine |
| `KivyMD` | Material Design widget library on top of Kivy |
| `Buildozer` | Automates Android SDK/NDK setup and APK/AAB packaging |
| `sqlite3` (stdlib) | Local history + settings persistence, no server needed |
| `pytest` | Unit testing the calculation engines |

---

## 10. Design highlights

- **Safe expression evaluation**: `app/utils/calculations.py` parses expressions with
  Python's `ast` module and only permits a whitelisted set of operators, function names,
  and constants — `eval()`/`exec()` are never used on user input.
- **Extensible GPA system**: `app/data/grade_scales.py` defines `GradeScale` objects
  (4.0 / 5.0 / 10.0 / percentage-based presets included) that are passed into the GPA
  engine. Adding a specific university's scale requires zero changes to
  `app/calculators/gpa.py`.
- **Configurable grade boundaries**: `GradeBoundaryTable` in the same module lets the
  Grade Calculator's mark-to-letter mapping be swapped without touching
  `app/calculators/grade.py`.
- **Modular unit converter**: each category (`Length`, `Weight`, `Temperature`, `Area`,
  `Volume`, `Time`, `Speed`, `Data Storage`) is a small factor table; `Temperature` alone
  needs an affine conversion, handled separately. New units/categories are one dict entry.
- **Graceful error handling**: every calculator validates input and shows a KivyMD dialog
  on invalid data (empty fields, division by zero, negative/zero credit hours, marks
  exceeding total, unrecognized grades, overflow, etc.) — the app is designed to never
  crash from normal user input.
- **Local-only persistence**: `app/utils/storage.py` wraps SQLite for calculation history
  (view / delete individual entries / clear all) and settings (theme, precision, default
  GPA scale) — no server, no network calls anywhere in the app.

---

## 11. Verification performed in this environment

This sandbox has no Android device/emulator, but the app was verified as far as possible
without one:

- **`python3 -m pytest tests/ -v`** — all 64 calculation-engine unit tests pass.
- **Headless UI smoke tests** (built and then removed from the final deliverable, since
  they were dev-only scratch scripts) were run under `Xvfb` with real `Kivy`/`KivyMD`
  installed, and confirmed:
  - Every screen (`home`, all 10 calculator screens, `settings`, `history`) builds and
    the `ScreenManager` can navigate to each of them without KV/wiring errors.
  - Real button-press interactions work end-to-end, e.g. Simple Calculator `12+5=17`,
    Scientific Calculator `sin(90)=1` in DEG mode, GPA/CGPA add-course/add-semester +
    calculate flows, Percentage/Grade/Average/Unit-Converter calculations, and that an
    intentionally invalid input (marks exceeding total) is caught and shown as a dialog
    instead of crashing.
  - The Home screen's search bar correctly filters cards (e.g. searching "gpa" surfaces
    the GPA/CGPA/Grade cards).
  - Calculations are correctly written to and read back from the SQLite history table.
  - The Android hardware/gesture back-button handler (`on_keyboard`, key code 27)
    correctly navigates back to Home from any other screen.

## 12. Limitations & assumptions

- **No physical Android build was produced here** — this environment has no Android
  SDK/NDK or emulator, and packaging an APK/AAB requires several GB of tooling and
  network access to Google's Maven/SDK repositories that this sandbox doesn't have.
  `buildozer.spec` is fully configured; running `buildozer -v android debug` on a real
  machine (per section 6) will produce an installable APK.
- **KivyMD version pinned to 1.2.0.** It prints a deprecation notice pointing at the
  KivyMD 2.x master branch (a significant, differently-namespaced widget API). 1.2.0 was
  chosen deliberately because its widget set (`MDRaisedButton`, `MDFlatButton`,
  `MDTopAppBar`, `MDTextField`, `MDCard`, `MDDropdownMenu`, etc.) is the stable,
  widely-documented API this project's `kv/` files and screens are written against. If
  you want KivyMD 2.x instead, the button/toolbar/menu class names and some KV
  properties will need updating to match its new API.
- **No custom icon/presplash assets** are bundled (`assets/icons`, `assets/images` are
  present but empty) — `buildozer.spec` has the `icon.filename` / `presplash.filename`
  keys ready to uncomment once you add real artwork; Material icon *names* (e.g.
  `"calculator"`, `"school"`) are used via KivyMD's built-in icon font in the meantime.
- **Fraction/decimal conversion** on the scientific calculator is implemented
  (`ScientificCalculator.as_fraction()` / `to_fraction_string()`), but no dedicated
  keypad button is wired to it in `kv/calculator.kv` — call it programmatically or add a
  button calling `root.engine.as_fraction()` if you want it exposed directly in the UI.
