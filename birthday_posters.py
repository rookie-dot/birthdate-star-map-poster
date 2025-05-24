import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Circle
from skyfield.api import Loader, Topos, Star
from skyfield.data import hipparcos
import requests
import json
from datetime import datetime, timedelta

# === FONT SETUP ===
mpl.rcParams['font.family'] = 'Gabriola'

# === DARK COLOR PALETTE ===
main_bg_color = '#0b0c1a'           # very dark navy / almost black, background of entire figure
map_bg_color = '#121630'            # dark blue navy, map background
border_color = '#445577'            # cool, dark blue for the border
border_width = 2.0

star_color = '#aabbff'              # light, cool blue for stars
star_color_bright = '#ffffff'       # bright white for the brightest stars

constellation_line_color = '#8899cc'   # soft blue for constellation lines
constellation_text_color = '#ccddee'   # bright, muted blue for constellation names

direction_text_color = '#ddeeff'       # very light, slightly bluish color for direction letters
degree_text_color = '#aabbcc'          # muted, cool color for degree labels

# === CONFIGURATION ===
birth_local = '2024-06-04 12:30'
dt_local = datetime.strptime(birth_local, '%Y-%m-%d %H:%M')
dt_utc = dt_local - timedelta(hours=2)
birth_datetime_utc = dt_utc.strftime('%Y-%m-%d %H:%M')

topo_lat, topo_lon = '53.8000 N', '20.5099 E'
topos = Topos(topo_lat, topo_lon)
mag_limit = 10.0

load = Loader('./skyfield-data')
ts = load.timescale()
year, month, day, hour, minute = map(int, birth_datetime_utc.replace('-', ' ').replace(':', ' ').split())
t = ts.utc(year, month, day, hour, minute)
planets = load('de421.bsp')

with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f)
star_objs = Star.from_dataframe(stars)
earth_obs = (planets['earth'] + topos).at(t)

apparent = earth_obs.observe(star_objs).apparent()
alt, az, _ = apparent.altaz()
mask = (alt.degrees > 0) & (stars['magnitude'] <= mag_limit)
alt_vis = alt.degrees[mask]
az_vis = az.degrees[mask]
mag_vis = stars['magnitude'][mask]

r_vals = 90 - alt_vis
theta_vals = np.radians(az_vis)

def get_constellation_lines():
    data = requests.get(
        'https://raw.githubusercontent.com/ofrohn/d3-celestial/master/data/constellations.lines.json'
    ).json()
    segs = []
    for feat in data['features']:
        for multi in feat['geometry']['coordinates']:
            for i in range(len(multi)-1):
                ra1, dec1 = multi[i]
                ra2, dec2 = multi[i+1]
                segs.append(((ra1, dec1), (ra2, dec2)))
    return segs

names_data = requests.get(
    'https://raw.githubusercontent.com/ofrohn/d3-celestial/master/data/constellations.json'
).json()

polish_constellations = {
  "And": "Andromeda",
  "Ant": "Antlia",
  "Aps": "Bird of Paradise",
  "Aqr": "Aquarius",
  "Aql": "Aquila",
  "Ara": "Altar",
  "Ari": "Aries",
  "Aur": "Auriga",
  "Boo": "Boötes",
  "Cae": "Caelum",
  "Cam": "Camelopardalis",
  "Cnc": "Cancer",
  "CVn": "Canes Venatici",
  "CMa": "Canis Major",
  "CMi": "Canis Minor",
  "Cap": "Capricornus",
  "Car": "Carina",
  "Cas": "Cassiopeia",
  "Cen": "Centaurus",
  "Cep": "Cepheus",
  "Cet": "Cetus",
  "Cha": "Chamaeleon",
  "Cir": "Circinus",
  "Col": "Columba",
  "Com": "Coma Berenices",
  "CrA": "Corona Australis",
  "CrB": "Corona Borealis",
  "Crv": "Corvus",
  "Crt": "Crater",
  "Cru": "Crux",
  "Cyg": "Cygnus",
  "Del": "Delphinus",
  "Dor": "Dorado",
  "Dra": "Draco",
  "Equ": "Equuleus",
  "Eri": "Eridanus",
  "For": "Fornax",
  "Gem": "Gemini",
  "Gru": "Grus",
  "Her": "Hercules",
  "Hor": "Horologium",
  "Hya": "Hydra",
  "Hyi": "Hydrus",
  "Ind": "Indus",
  "Lac": "Lacerta",
  "Leo": "Leo",
  "LMi": "Leo Minor",
  "Lep": "Lepus",
  "Lib": "Libra",
  "Lup": "Lupus",
  "Lyn": "Lynx",
  "Lyr": "Lyra",
  "Men": "Mensa",
  "Mic": "Microscopium",
  "Mon": "Monoceros",
  "Mus": "Musca",
  "Nor": "Norma",
  "Oct": "Octans",
  "Oph": "Ophiuchus",
  "Ori": "Orion",
  "Pav": "Pavo",
  "Peg": "Pegasus",
  "Per": "Perseus",
  "Phe": "Phoenix",
  "Pic": "Pictor",
  "Psc": "Pisces",
  "PsA": "Piscis Austrinus",
  "Pup": "Puppis",
  "Pyx": "Pyxis",
  "Ret": "Reticulum",
  "Sge": "Sagitta",
  "Sgr": "Sagittarius",
  "Sco": "Scorpius",
  "Scl": "Sculptor",
  "Sct": "Scutum",
  "Ser": "Serpens",
  "Sex": "Sextans",
  "Tau": "Taurus",
  "Tel": "Telescopium",
  "Tri": "Triangulum",
  "TrA": "Triangulum Australe",
  "Tuc": "Tucana",
  "UMa": "Ursa Major",
  "UMi": "Ursa Minor",
  "Vel": "Vela",
  "Vir": "Virgo",
  "Vol": "Volans",
  "Vul": "Vulpecula"
}

def plot_star_map(filename, with_constellations=False):
    fig, ax = plt.subplots(figsize=(12,12), subplot_kw={'projection':'polar'})
    fig.patch.set_facecolor(main_bg_color)
    ax.set_facecolor(map_bg_color)

    ax.set_theta_zero_location('N')
    ax.set_theta_direction(1)
    ax.set_rlim(0, 94)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)

    outer_circle = Circle((0,0), 90, transform=ax.transData._b,
                          fill=False, color=border_color, lw=border_width)
    ax.add_patch(outer_circle)

    directions = {'N': 0, 'E': 90, 'S': 180, 'W': 270}
    for label, angle in directions.items():
        ax.text(np.radians(angle), 90 + 2, label, ha='center', va='center',
                fontsize=12, color=direction_text_color, fontweight='bold',
                rotation=angle, rotation_mode='anchor')

    for angle in range(0, 360, 10):
        if angle not in directions.values():
            ax.text(np.radians(angle), 90 + 2, f"{angle}°", ha='center', va='center',
                    fontsize=10, color=degree_text_color, rotation=angle, rotation_mode='anchor')

    sizes = 100 * 10**(-mag_vis/2.5)
    bright = mag_vis <= 2.0
    sizes[bright] *= 0.3
    colors = np.where(bright, star_color_bright, star_color)
    ax.scatter(theta_vals, r_vals, s=sizes, c=colors, alpha=1, edgecolors='none')

    if with_constellations:
        for (ra1, dec1),(ra2, dec2) in get_constellation_lines():
            s1 = Star(ra_hours=ra1/15, dec_degrees=dec1)
            s2 = Star(ra_hours=ra2/15, dec_degrees=dec2)
            a1 = earth_obs.observe(s1).apparent().altaz()
            a2 = earth_obs.observe(s2).apparent().altaz()
            if a1[0].degrees > 0 and a2[0].degrees > 0:
                r1, r2 = 90 - a1[0].degrees, 90 - a2[0].degrees
                t1, t2 = np.radians(a1[1].degrees), np.radians(a2[1].degrees)
                ax.plot([t1, t2], [r1, r2], color=constellation_line_color, lw=0.6)

        for feature in names_data['features']:
            cs_id = feature['id']
            ra_deg, dec_deg = feature['geometry']['coordinates']
            cs = Star(ra_hours=ra_deg/15, dec_degrees=dec_deg)
            ac = earth_obs.observe(cs).apparent().altaz()
            if ac[0].degrees > 0:
                offset = 3
                r_c = max(0, 90 - ac[0].degrees - offset)
                t_c = np.radians(ac[1].degrees)
                name_pl = polish_constellations.get(cs_id, cs_id)
                ax.text(t_c, r_c, name_pl, fontsize=8, color=constellation_text_color,
                        ha='center', va='bottom')

    plt.tight_layout()
    fig.savefig(filename, dpi=300, facecolor=main_bg_color)
    plt.close()

plot_star_map('stars_only_dark.png', False)
plot_star_map('with_constellations_dark.png', True)
