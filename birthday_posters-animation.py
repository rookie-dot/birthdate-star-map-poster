import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Circle
from skyfield.api import Loader, Topos, Star
from skyfield.data import hipparcos
from datetime import timedelta
import requests
import imageio

# === Font and color settings ===
mpl.rcParams['font.family'] = 'Gabriola'

main_bg_color = '#0b0c1a'
map_bg_color = '#121630'
border_color = '#445577'
border_width = 2.0
star_color = '#aabbff'
star_color_bright = '#ffffff'
constellation_line_color = "#8899cc"
constellation_text_color = '#ccddee'
direction_text_color = '#ddeeff'
degree_text_color = '#aabbcc'

magnitude_limit = 10.0
observer_lat, observer_lon = '53.8000 N', '20.5099 E'
observer_location = Topos(observer_lat, observer_lon)

load = Loader('./skyfield-data')
ts = load.timescale()
planets = load('de421.bsp')

with load.open(hipparcos.URL) as f:
    stars = hipparcos.load_dataframe(f)
star_objects = Star.from_dataframe(stars)

# Fetch constellation line data (with caching)
def get_constellation_lines():
    url = 'https://raw.githubusercontent.com/ofrohn/d3-celestial/master/data/constellations.lines.json'
    data = requests.get(url).json()
    segments = []
    for feature in data['features']:
        for multi_line in feature['geometry']['coordinates']:
            for i in range(len(multi_line)-1):
                ra1, dec1 = multi_line[i]
                ra2, dec2 = multi_line[i+1]
                segments.append(((ra1, dec1), (ra2, dec2)))
    return segments

constellation_lines = get_constellation_lines()

# Constellation names data
names_data = requests.get(
    'https://raw.githubusercontent.com/ofrohn/d3-celestial/master/data/constellations.json'
).json()

polish_to_english_constellations = {
  "And": "Andromeda",
  "Ant": "Pump",
  "Aps": "Bird of Paradise",
  "Aqr": "Aquarius",
  "Aql": "Eagle",
  "Ara": "Altar",
  "Ari": "Aries",
  "Aur": "Charioteer",
  "Boo": "Boötes",
  "Cae": "Chisel",
  "Cam": "Camelopardalis",
  "Cnc": "Cancer",
  "CVn": "Canes Venatici",
  "CMa": "Canis Major",
  "CMi": "Canis Minor",
  "Cap": "Capricorn",
  "Car": "Keel",
  "Cas": "Cassiopeia",
  "Cen": "Centaurus",
  "Cep": "Cepheus",
  "Cet": "Cetus",
  "Cha": "Chamaeleon",
  "Cir": "Circinus",
  "Col": "Dove",
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

def plot_star_map_at_time(time, filename):
    earth_observer = (planets['earth'] + observer_location).at(time)
    apparent = earth_observer.observe(star_objects).apparent()
    alt, az, _ = apparent.altaz()
    visible_mask = (alt.degrees > 0) & (stars['magnitude'] <= magnitude_limit)
    alt_visible = alt.degrees[visible_mask]
    az_visible = az.degrees[visible_mask]
    mag_visible = stars['magnitude'][visible_mask]

    r_values = 90 - alt_visible
    theta_values = np.radians(az_visible)

    fig, ax = plt.subplots(figsize=(8,8), subplot_kw={'projection':'polar'})
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

    # Stars
    sizes = 100 * 10**(-mag_visible/2.5)
    bright_stars = mag_visible <= 2.0
    sizes[bright_stars] *= 0.3
    colors = np.where(bright_stars, star_color_bright, star_color)
    ax.scatter(theta_values, r_values, s=sizes, c=colors, alpha=1, edgecolors='none')

    # Constellation lines
    for (ra1, dec1), (ra2, dec2) in constellation_lines:
        star1 = Star(ra_hours=ra1/15, dec_degrees=dec1)
        star2 = Star(ra_hours=ra2/15, dec_degrees=dec2)
        a1 = earth_observer.observe(star1).apparent().altaz()
        a2 = earth_observer.observe(star2).apparent().altaz()
        if a1[0].degrees > 0 and a2[0].degrees > 0:
            r1, r2 = 90 - a1[0].degrees, 90 - a2[0].degrees
            t1, t2 = np.radians(a1[1].degrees), np.radians(a2[1].degrees)
            ax.plot([t1, t2], [r1, r2], color=constellation_line_color, lw=0.6)

    # Constellation names
    for feature in names_data['features']:
        cs_id = feature['id']
        ra_deg, dec_deg = feature['geometry']['coordinates']
        cs_star = Star(ra_hours=ra_deg/15, dec_degrees=dec_deg)
        ac = earth_observer.observe(cs_star).apparent().altaz()
        if ac[0].degrees > 0:
            offset = 3
            r_c = max(0, 90 - ac[0].degrees - offset)
            t_c = np.radians(ac[1].degrees)
            name_en = polish_to_english_constellations.get(cs_id, cs_id)
            ax.text(t_c, r_c, name_en, fontsize=8, color=constellation_text_color,
                    ha='center', va='bottom')

    plt.tight_layout()
    fig.savefig(filename, dpi=150, facecolor=main_bg_color)
    plt.close()

# === Main loop and folder creation ===
output_dir = 'gif'
os.makedirs(output_dir, exist_ok=True)

start_time = ts.utc(2024, 6, 4, 22, 0)
frames = []
filenames = []

for i in range(144):
    current_time = ts.utc(2024, 6, 4, 22, 0) + timedelta(minutes=10*i)
    fname = os.path.join(output_dir, f'frame_{i:03d}.png')
    plot_star_map_at_time(current_time, fname)
    filenames.append(fname)

# Create GIF animation
with imageio.get_writer(os.path.join(output_dir, 'night_sky_animation.gif'), mode='I', duration=0.2) as writer:
    for fname in filenames:
        image = imageio.imread(fname)
        writer.append_data(image)

print(f"Animation saved in directory {output_dir}/night_sky_animation.gif")
