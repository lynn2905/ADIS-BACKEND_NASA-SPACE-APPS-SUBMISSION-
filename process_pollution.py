"""
Process fused_data.json and generate visualizations for ADIS globe
Reads pollution data and creates heatmap overlays
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd

def load_fused_data(filepath='fused_data.json'):
    """Load and parse the fused pollution dataset"""
    print(f"Loading data from {filepath}...")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Convert to DataFrame for easier processing
    df = pd.DataFrame(data)
    
    # Filter out invalid NO2 values
    df_valid = df[df['NO2'] > -1e20].copy()
    
    print(f"Total records: {len(df)}")
    print(f"Valid NO2 measurements: {len(df_valid)}")
    print(f"Anomalies detected: {df['anomaly_flag'].sum()}")
    
    return df, df_valid

def calculate_aqi_from_no2(no2_values):
    """
    Convert NO2 concentration to AQI-like scale
    NO2 is in molecules/cm² from satellite data
    """
    # Scale NO2 to AQI range (simplified)
    # Typical NO2 ranges: 1e14 to 1e16 molecules/cm²
    aqi = np.clip(no2_values * 1e-14 * 50, 0, 500)
    return aqi

def get_aqi_color(aqi):
    """Return RGB color based on AQI value"""
    if aqi <= 50:
        return (0, 228, 0)  # Green
    elif aqi <= 100:
        return (255, 255, 0)  # Yellow
    elif aqi <= 150:
        return (255, 126, 0)  # Orange
    elif aqi <= 200:
        return (255, 0, 0)  # Red
    elif aqi <= 300:
        return (143, 63, 151)  # Purple
    else:
        return (126, 0, 35)  # Maroon

def create_global_heatmap(df_valid, output_file='globe_pollution_heatmap.png'):
    """
    Create a global heatmap visualization of pollution data
    """
    print("\nGenerating global heatmap...")
    
    # Calculate AQI from NO2
    df_valid['aqi'] = calculate_aqi_from_no2(df_valid['NO2'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 8), facecolor='#0a1628')
    ax.set_facecolor('#0a1628')
    
    # Create custom colormap (AQI colors)
    colors = ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#8f3f97', '#7e0023']
    n_bins = 6
    cmap = LinearSegmentedColormap.from_list('aqi', colors, N=n_bins)
    
    # Plot as scatter with color based on AQI
    scatter = ax.scatter(
        df_valid['lon'], 
        df_valid['lat'], 
        c=df_valid['aqi'],
        cmap=cmap,
        s=1,
        alpha=0.6,
        vmin=0,
        vmax=300
    )
    
    # Highlight anomalies
    anomalies = df_valid[df_valid['anomaly_flag'] == 1]
    if len(anomalies) > 0:
        ax.scatter(
            anomalies['lon'],
            anomalies['lat'],
            c='red',
            s=20,
            marker='x',
            alpha=0.8,
            label=f'Anomalies ({len(anomalies)})'
        )
    
    # Styling
    ax.set_xlabel('Longitude', color='white', fontsize=12)
    ax.set_ylabel('Latitude', color='white', fontsize=12)
    ax.set_title('Global Pollution Heatmap (NO2 Concentrations)', 
                 color='white', fontsize=16, pad=20)
    ax.grid(True, alpha=0.2, color='white')
    ax.tick_params(colors='white')
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, label='Air Quality Index (AQI)')
    cbar.set_label('Air Quality Index (AQI)', color='white')
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
    
    if len(anomalies) > 0:
        ax.legend(loc='upper right', facecolor='#1a2332', 
                 edgecolor='white', labelcolor='white')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, facecolor='#0a1628', 
                bbox_inches='tight')
    print(f"Saved: {output_file}")
    
    return fig

def create_regional_zoom(df_valid, center_lat, center_lon, 
                        radius=10, output_file='regional_zoom.png'):
    """
    Create zoomed-in view of specific region
    """
    print(f"\nGenerating regional zoom around ({center_lat}, {center_lon})...")
    
    # Filter data within radius
    lat_min, lat_max = center_lat - radius, center_lat + radius
    lon_min, lon_max = center_lon - radius, center_lon + radius
    
    regional = df_valid[
        (df_valid['lat'] >= lat_min) & (df_valid['lat'] <= lat_max) &
        (df_valid['lon'] >= lon_min) & (df_valid['lon'] <= lon_max)
    ]
    
    if len(regional) == 0:
        print(f"No data found in region ({lat_min}, {lon_min}) to ({lat_max}, {lon_max})")
        return None
    
    print(f"Found {len(regional)} data points in region")
    
    # Calculate AQI
    regional['aqi'] = calculate_aqi_from_no2(regional['NO2'])
    
    fig, ax = plt.subplots(figsize=(12, 10), facecolor='#0a1628')
    ax.set_facecolor('#0a1628')
    
    # Plot pollution levels
    colors = ['#00e400', '#ffff00', '#ff7e00', '#ff0000', '#8f3f97', '#7e0023']
    cmap = LinearSegmentedColormap.from_list('aqi', colors, N=6)
    
    scatter = ax.scatter(
        regional['lon'],
        regional['lat'],
        c=regional['aqi'],
        cmap=cmap,
        s=50,
        alpha=0.7,
        vmin=0,
        vmax=300
    )
    
    # Highlight anomalies
    anomalies = regional[regional['anomaly_flag'] == 1]
    if len(anomalies) > 0:
        ax.scatter(
            anomalies['lon'],
            anomalies['lat'],
            c='red',
            s=200,
            marker='*',
            edgecolors='white',
            linewidths=2,
            alpha=0.9,
            label=f'Anomalies ({len(anomalies)})',
            zorder=10
        )
    
    ax.set_xlabel('Longitude', color='white', fontsize=12)
    ax.set_ylabel('Latitude', color='white', fontsize=12)
    ax.set_title(f'Regional Detail: ({center_lat}°, {center_lon}°)', 
                 color='white', fontsize=16, pad=20)
    ax.grid(True, alpha=0.3, color='white')
    ax.tick_params(colors='white')
    
    cbar = plt.colorbar(scatter, ax=ax, label='AQI')
    cbar.set_label('Air Quality Index (AQI)', color='white')
    cbar.ax.yaxis.set_tick_params(color='white')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
    
    if len(anomalies) > 0:
        ax.legend(loc='upper right', facecolor='#1a2332',
                 edgecolor='white', labelcolor='white')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, facecolor='#0a1628',
                bbox_inches='tight')
    print(f"Saved: {output_file}")
    
    return fig

def export_for_web_globe(df_valid, output_file='globe_data.json'):
    """
    Export processed data in format suitable for web globe
    """
    print(f"\nExporting data for web visualization...")
    
    # Calculate AQI
    df_valid['aqi'] = calculate_aqi_from_no2(df_valid['NO2'])
    
    # Sample data if too large (>50k points)
    if len(df_valid) > 50000:
        print(f"Sampling {len(df_valid)} points to 50,000 for performance...")
        df_export = df_valid.sample(n=50000, random_state=42)
    else:
        df_export = df_valid
    
    # Create export format
    export_data = []
    for _, row in df_export.iterrows():
        export_data.append({
            'lat': float(row['lat']),
            'lon': float(row['lon']),
            'aqi': float(row['aqi']),
            'no2': float(row['NO2']),
            'anomaly': int(row['anomaly_flag']),
            'temp': float(row['T2M']) if 'T2M' in row else None,
        })
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f)
    
    print(f"Saved: {output_file} ({len(export_data)} points)")
    return export_data

def generate_statistics_report(df, df_valid):
    """
    Generate statistical summary of the dataset
    """
    print("\n" + "="*70)
    print("POLLUTION DATA ANALYSIS REPORT")
    print("="*70)
    
    print(f"\nDataset Overview:")
    print(f"  Total records: {len(df):,}")
    print(f"  Valid NO2 measurements: {len(df_valid):,}")
    print(f"  Data coverage: {len(df_valid)/len(df)*100:.1f}%")
    
    print(f"\nGeographic Coverage:")
    print(f"  Latitude range: {df_valid['lat'].min():.2f}° to {df_valid['lat'].max():.2f}°")
    print(f"  Longitude range: {df_valid['lon'].min():.2f}° to {df_valid['lon'].max():.2f}°")
    
    print(f"\nPollution Metrics:")
    print(f"  NO2 mean: {df_valid['NO2'].mean():.2e} molecules/cm²")
    print(f"  NO2 std: {df_valid['NO2'].std():.2e} molecules/cm²")
    print(f"  NO2 min: {df_valid['NO2'].min():.2e} molecules/cm²")
    print(f"  NO2 max: {df_valid['NO2'].max():.2e} molecules/cm²")
    
    # Calculate AQI statistics
    aqi_values = calculate_aqi_from_no2(df_valid['NO2'])
    print(f"\nAir Quality Index (Estimated):")
    print(f"  Mean AQI: {aqi_values.mean():.1f}")
    print(f"  Good (0-50): {(aqi_values <= 50).sum():,} points ({(aqi_values <= 50).sum()/len(aqi_values)*100:.1f}%)")
    print(f"  Moderate (51-100): {((aqi_values > 50) & (aqi_values <= 100)).sum():,} points")
    print(f"  Unhealthy (101-200): {((aqi_values > 100) & (aqi_values <= 200)).sum():,} points")
    print(f"  Very Unhealthy (201+): {(aqi_values > 200).sum():,} points")
    
    print(f"\nAnomaly Detection:")
    print(f"  Total anomalies: {df['anomaly_flag'].sum():,}")
    print(f"  Anomaly rate: {df['anomaly_flag'].sum()/len(df)*100:.2f}%")
    
    if 'T2M' in df.columns:
        print(f"\nMeteorological Data:")
        print(f"  Temperature mean: {df_valid['T2M'].mean()-273.15:.1f}°C")
        print(f"  Temperature range: {df_valid['T2M'].min()-273.15:.1f}°C to {df_valid['T2M'].max()-273.15:.1f}°C")
    
    print("\n" + "="*70)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Load data
    df_all, df_valid = load_fused_data('fused_data.json')
    
    # Generate statistics
    generate_statistics_report(df_all, df_valid)
    
    # Create visualizations
    create_global_heatmap(df_valid, 'globe_pollution_heatmap.png')
    
    # Export for web globe
    export_for_web_globe(df_valid, 'globe_data.json')
    
    # Optional: Create regional zooms for hotspots
    # Find regions with highest pollution
    df_valid['aqi'] = calculate_aqi_from_no2(df_valid['NO2'])
    hotspots = df_valid.nlargest(5, 'aqi')
    
    print("\nTop 5 Pollution Hotspots:")
    for i, row in hotspots.iterrows():
        print(f"  {i+1}. Lat: {row['lat']:.2f}, Lon: {row['lon']:.2f}, AQI: {row['aqi']:.1f}")
    
    # Create zoom for highest pollution area
    if len(hotspots) > 0:
        top_spot = hotspots.iloc[0]
        create_regional_zoom(df_valid, top_spot['lat'], top_spot['lon'],
                           radius=5, output_file='hotspot_zoom.png')
    
    print("\n" + "="*70)
    print("✅ PROCESSING COMPLETE")
    print("="*70)
    print("\nGenerated files:")
    print("  📊 globe_pollution_heatmap.png - Global heatmap visualization")
    print("  📍 hotspot_zoom.png - Zoomed view of highest pollution area")
    print("  📦 globe_data.json - Processed data for web globe (50k points)")
    print("\nTo use in your React app:")
    print("  1. Copy globe_data.json to your React app's public/ directory")
    print("  2. Fetch it in your app with: fetch('/globe_data.json')")
    print("  3. Use the lat, lon, aqi fields to render colored markers")
    print("="*70)