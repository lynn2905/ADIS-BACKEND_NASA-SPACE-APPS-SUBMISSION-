import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# ------------------------
# Step 1 — Load the data
# ------------------------
file_path = "./data/TEMPO_NO2_L2_V03_20250406T215103Z_S012G07.nc"
print(f"Opening file: {file_path}")

# Open dataset
datatree = xr.open_datatree(file_path)
print("✅ File opened successfully!")
print(datatree)

# ------------------------
# Step 2 — Select the NO₂ variable
# ------------------------
product_variable_name = "product/vertical_column_troposphere"
da = datatree[product_variable_name]
print("✅ Variable loaded:", product_variable_name)
print(da)

# ------------------------
# Step 3 — Set up map projection
# ------------------------
data_proj = ccrs.PlateCarree()

def make_nice_map(axis):
    axis.add_feature(cfeature.COASTLINE, linewidth=0.5, color="gray")
    axis.add_feature(cfeature.BORDERS, linewidth=0.5, color="gray")
    axis.add_feature(cfeature.STATES, linewidth=0.2, color="gray")
    axis.set_extent([-150, -40, 14, 65], crs=data_proj)
    grid = axis.gridlines(draw_labels=["left", "bottom"], dms=True)
    grid.xformatter = LONGITUDE_FORMATTER
    grid.yformatter = LATITUDE_FORMATTER

# ------------------------
# Step 4 — Create visualization
# ------------------------
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": data_proj})
make_nice_map(ax)

contour = ax.contourf(
    datatree["geolocation/longitude"],
    datatree["geolocation/latitude"],
    da.where(datatree["product/main_data_quality_flag"] == 0),
    levels=100,
    transform=data_proj
)

cb = plt.colorbar(contour)
cb.set_label("Tropospheric Nitrogen Dioxide Vertical Column [molecules/cm²]")

plt.title("NASA TEMPO — NO₂ Vertical Column (Sample Data)")
plt.show()
