# config.py
# --------------------------------------------------------
# ADIS (Atmospheric Digital Immune System) Configuration
# --------------------------------------------------------

# === Server Configuration ===
HOST = "127.0.0.1"   # Localhost for development
PORT = 8000          # Flask API port
DEBUG = True         # Enable debug mode for auto-reload

# === File Paths ===
FUSED_JSON = "./data/fused_data.json"
FUSED_CSV = "./data/fused_data.csv"

# === Column Mappings ===
LAT_COL = "lat"              # Latitude column
LON_COL = "lon"              # Longitude column
NO2_COL = "NO2"              # Nitrogen Dioxide concentration
T2M_COL = "T2M"              # Temperature at 2 meters
QV2M_COL = "QV2M"            # Specific humidity at 2 meters
PS_COL = "PS"                # Surface pressure
ANOM_COL = "anomaly_flag"    # Detected anomaly flag

# === Anomaly Detection Thresholds ===
Z_CUTOFF = 2.0       # Z-score threshold for anomaly detection
MIN_NO2 = 1e14       # Ignore unrealistically low NO2 values

# === Meteorological Defaults (used if missing from dataset) ===
FALLBACK_WIND = (2.0, 1.0)   # (U, V) -> eastward & northward components (m/s)
WIND_SPEED_M_S = 5.0         # Default mean transport wind speed
WIND_DIR_DEG = 270           # Default wind direction (from west to east)

# === Diffusion / Turbulence Settings ===
DIFFUSION_KM = 5.0      # Lateral spread (km per sqrt(hour))
DEFAULT_HOURS = 6       # Forecast duration (hours)
TIME_STEP_MIN = 10      # Minutes between plume path points

# === Display / Debugging ===
PRINT_LOGS = True        # Whether to show extra debug info in terminal
VERBOSE = False          # Set to True to log every computation step

# === Derived constants ===
EARTH_RADIUS_KM = 6371.0       # Earth radius (km)
DEG_PER_KM = 1.0 / 111.0       # Degree distance per km (approx)
