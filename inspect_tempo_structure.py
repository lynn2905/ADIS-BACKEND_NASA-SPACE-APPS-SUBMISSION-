import h5py

file_path = "./data/TEMPO_NO2_L2_V03_20250406T215103Z_S012G07.nc"

with h5py.File(file_path, "r") as f:
    print("\n📂 File structure:\n")

    def print_structure(name, obj):
        if isinstance(obj, h5py.Dataset):
            print(f"  📊 Dataset: {name} -> shape: {obj.shape}")
        elif isinstance(obj, h5py.Group):
            print(f"📁 Group: {name}")

    f.visititems(print_structure)
