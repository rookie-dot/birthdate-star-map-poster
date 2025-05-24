# Star Map Generator

This Python script generates a polar star map visualization for a specified date, time, and location in Poland. It plots stars from the Hipparcos catalog, with optional constellation lines and names displayed in Polish, all styled with a dark color palette.

---

## Features

- Plots stars visible above the horizon at a given UTC datetime and location.
- Uses Hipparcos star catalog with configurable magnitude limit.
- Displays constellation lines and names in Polish (optional).
- Beautiful dark-themed color scheme with clear star brightness differentiation.
- Saves output as high-resolution PNG images.

---

## Requirements

- Python 3.x
- Libraries:
  - `numpy`
  - `matplotlib`
  - `skyfield`
  - `requests`
  - `datetime` (built-in)

Install dependencies via pip:

```bash
pip3 install numpy matplotlib skyfield requests
````

---

## Configuration

Inside the script, you can configure:

* `birth_local`: Local datetime string (format `'YYYY-MM-DD HH:MM'`) to generate the sky map for.
* `topo_lat`, `topo_lon`: Geographic coordinates of the observation point (latitude and longitude as strings, e.g., `'53.8000 N'`, `'20.5099 E'`).
* `mag_limit`: Magnitude limit for stars to be shown (default is 10.0).

Example configuration:

```python
birth_local = '2024-06-04 12:30'
topo_lat, topo_lon = '53.8000 N', '20.5099 E'
mag_limit = 10.0
```

---

## Usage

Run the script directly with Python:

```bash
python3 birthday_posters.py
```

It will generate two PNG files in the working directory:

* `stars_only_dark.png` — star map with stars only.
* `with_constellations_dark.png` — star map with stars plus constellation lines and Polish constellation names.

---

## How It Works

* Converts the local datetime to UTC.
* Loads star data from the Hipparcos catalog.
* Calculates visible stars above the horizon for the given time and location.
* Plots stars on a polar plot where radius represents zenith distance (90° - altitude) and angle is azimuth.
* Optionally overlays constellation lines and names fetched from online JSON sources.
* Uses a dark, navy-blue themed color palette for aesthetics and readability.
* Saves the plots as PNG files with a transparent background matching the theme.

---

## Notes

* The script downloads constellation data from the internet each time it runs; ensure you have an active internet connection.
* The font "Gabriola" is set as default in the script. If not installed on your system, you may change it or use the default font by modifying the matplotlib rcParams.
* The magnitude-based star sizing gives brighter stars larger sizes and a distinct color.

---

## License

This project is provided for personal and educational use.
