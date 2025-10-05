
import datetime as dt
import getpass

import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from xarray.plot.utils import label_from_attrs

from harmony import BBox, Client, Collection, Request
from harmony.config import Environment





# --------------------------
# STEP 2 — Retrieve TEMPO Data via Harmony (fixed version)
# --------------------------
from harmony import Client, Request, Collection
from harmony.config import Environment

print("Connecting to NASA Harmony using Earthdata credentials...")

# Initialize Harmony client using .netrc authentication
harmony_client = Client(env=Environment.PROD)

# Create a Collection object for TEMPO NO2 total column
collection = Collection(id="C2930725014-LARC_CLOUD")

# Choose an example granule
granule_name = ["TEMPO_NO2_L2_V03_20250406T215103Z_S012G07.nc"]

# Create the data request properly
request = Request(
    collection=collection,
    granule_name=granule_name
)

print("Submitting request...")
job_id = harmony_client.submit(request)
print(f"Job submitted: {job_id}")

# Wait for completion
harmony_client.wait_for_processing(job_id, show_progress=True)

# Download and save results
results = harmony_client.download_all(job_id, directory="./data")
all_results_stored = [f.result() for f in results]

print(f"Number of result files: {len(all_results_stored)}")
print("Saved files:")
for file in all_results_stored:
    print(file)
