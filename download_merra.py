import requests
from tqdm import tqdm
import xarray as xr

url = "https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/M2I1NXASM.5.12.4/2024/04/MERRA2_400.inst1_2d_asm_Nx.20240410.nc4"
output = "MERRA2_20240410.nc4"

session = requests.Session()
session.auth = ('your_username', 'your_password')

response = session.get(url, stream=True)
response.raise_for_status()

with open(output, "wb") as f:
    for chunk in tqdm(response.iter_content(chunk_size=8192)):
        if chunk:
            f.write(chunk)

print("✅ MERRA-2 download complete:", output)

# --- NEW CODE ---
ds = xr.open_dataset("MERRA2_20240410.nc4")
print(ds)
