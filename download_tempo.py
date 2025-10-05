# =======================================================
# ADIS – NASA TEMPO L2 Downloader
# Downloads TEMPO NO2 data (L2) automatically from NASA GES DISC
# Author: Mira Kabalan & ADIS Team
# =======================================================

import os
import requests
from tqdm import tqdm
from datetime import datetime, timedelta

# -----------------------------
# CONFIGURATION
# -----------------------------

# Base URL for TEMPO NO2 Level 2 Data
BASE_URL = "https://data.gesdisc.earthdata.nasa.gov/data/TEMPO_L2_NO2.001/"

# Output directory
OUTPUT_DIR = "tempo_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Earthdata credentials (must already exist in your ~/.netrc)
# Example .netrc content:
# machine urs.earthdata.nasa.gov
#     login your_email@example.com
#     password your_password

# Date range for downloads (you can adjust)
START_DATE = datetime(2024, 4, 10)
END_DATE   = datetime(2024, 4, 12)   # inclusive

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def download_file(session, url, dest):
    """Download one file with progress bar."""
    response = session.get(url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get("content-length", 0))
