"""
Sentinel-2 L2A NDVI Change Detection Pipeline
Solapur District, Maharashtra — Tile T43QEV
Dates: 31 Dec 2025 vs 16 March 2026

Usage:
    Edit the CONFIG section below with your local .SAFE folder paths.
    Then run:  python sentinel2_pipeline.py

Outputs (saved to ./outputs/):
    ndvi_dec2025.png
    ndvi_march2026.png
    histogram_31dec2025.png
    histogram_16march2026.png
    ndvi_histogram_31dec2025.png
    ndvi_histogram_16march2026.png
    spectral_signatures_31dec2025.png
    spectral_signatures_16march2026.png
    ndvi_change_detection.png
    ndvi_threshold_classified.png
"""

import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ── CONFIG ────────────────────────────────────────────────────────────────────
# Edit these two paths to point at your local .SAFE folders.
# Everything else runs automatically.

SAFE_DEC = (
    r"C:\Users\ashis\Downloads"
    r"\S2C_MSIL2A_20251231T052231_N0511_R062_T43QEV_20251231T083411.SAFE"
)
SAFE_MARCH = (
    r"C:\Users\ashis\Downloads"
    r"\S2B_MSIL2A_20260316T051649_N0512_R062_T43QEV_20260316T091005.SAFE"
)

# Tile ID — used to build band file paths inside the .SAFE structure
TILE_ID_DEC   = "T43QEV_20251231T052231"
TILE_ID_MARCH = "T43QEV_20260316T051649"
GRANULE_DEC   = "L2A_T43QEV_A006896_20251231T053319"
GRANULE_MARCH = "L2A_T43QEV_A047135_20260316T052630"

# Georeferenced sample points (UTM easting, northing) for spectral signatures.
# These are fixed for tile T43QEV — no need to change.
SAMPLE_POINTS = {
    "Water":      (596315, 1959919),
    "Urban":      (597336, 1952676),
    "Soil":       (591941, 1969797),
    "Vegetation": (552839, 1938202),
}

OUTPUT_DIR = "outputs"
# ─────────────────────────────────────────────────────────────────────────────


def band_path(safe_dir: str, granule: str, tile_id: str, band: str) -> str:
    """Build the full path to a 10m band JP2 file inside a .SAFE folder."""
    return os.path.join(
        safe_dir, "GRANULE", granule, "IMG_DATA", "R10m",
        f"{tile_id}_{band}_10m.jp2"
    )


def load_band(path: str) -> tuple[np.ndarray, rasterio.DatasetReader]:
    """
    Open a Sentinel-2 L2A band JP2, apply BOA reflectance correction,
    and mask physically invalid pixels.

    Returns corrected band array (float, NaN where invalid) and the open
    dataset (kept open for .index() coordinate lookups).
    """
    ds = rasterio.open(path)
    raw = ds.read(1).astype(float)

    # BOA reflectance: offset = -1000, quantification = 10000
    corrected = (raw - 1000) / 10000

    # Mask out-of-range values (clouds, saturated pixels, fill)
    corrected[(corrected > 1.0) | (corrected <= 0)] = np.nan
    return corrected, ds


def compute_ndvi(b04: np.ndarray, b08: np.ndarray) -> np.ndarray:
    """
    Compute NDVI = (NIR - Red) / (NIR + Red).
    Division-by-zero and out-of-range values are set to NaN.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = (b08 - b04) / (b08 + b04)
    ndvi[~np.isfinite(ndvi)] = np.nan
    ndvi[(ndvi < -1) | (ndvi > 1)] = np.nan
    return ndvi


def plot_ndvi_map(ndvi: np.ndarray, date_label: str, out_path: str) -> None:
    plt.figure(figsize=(8, 7))
    plt.imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
    plt.colorbar(label="NDVI")
    plt.title(f"NDVI — Solapur — {date_label}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.clf()
    plt.close()
    print(f"  Saved: {out_path}")


def plot_band_histogram(
    b04: np.ndarray, b08: np.ndarray, date_label: str, out_path: str
) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(b04[~np.isnan(b04)].ravel(), bins=100, color="tomato",
            alpha=0.65, label="B04 Red")
    ax.hist(b08[~np.isnan(b08)].ravel(), bins=100, color="darkred",
            alpha=0.65, label="B08 NIR")
    ax.set_title(f"Band Reflectance Distribution — Solapur — {date_label}")
    ax.set_xlabel("Surface Reflectance")
    ax.set_ylabel("Pixel Count")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.clf()
    plt.close()
    print(f"  Saved: {out_path}")


def plot_ndvi_histogram(ndvi: np.ndarray, date_label: str, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(ndvi[~np.isnan(ndvi)].ravel(), bins=200, color="forestgreen",
            edgecolor="none")
    ax.set_title(f"NDVI Distribution — Solapur — {date_label}")
    ax.set_xlabel("NDVI Value")
    ax.set_ylabel("Pixel Count")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.clf()
    plt.close()
    print(f"  Saved: {out_path}")


def extract_spectral_signatures(
    b04: np.ndarray,
    b08: np.ndarray,
    ds: rasterio.DatasetReader,
    sample_points: dict,
) -> dict:
    """
    Sample B04 and B08 reflectance at georeferenced UTM coordinates.
    Returns dict: {label: {"b04": float, "b08": float, "ndvi": float}}
    """
    results = {}
    for label, (east, north) in sample_points.items():
        row, col = ds.index(east, north)
        r = float(b04[row, col])
        n = float(b08[row, col])
        ndvi_val = (n - r) / (n + r) if (n + r) != 0 else np.nan
        results[label] = {"b04": r, "b08": n, "ndvi": ndvi_val}
        print(f"    {label:12s}  B04={r:.4f}  B08={n:.4f}  NDVI={ndvi_val:.4f}")
    return results


def plot_spectral_signatures(
    signatures: dict, date_label: str, out_path: str
) -> None:
    labels = list(signatures.keys())
    b04_vals = [signatures[l]["b04"] for l in labels]
    b08_vals = [signatures[l]["b08"] for l in labels]

    x = np.arange(len(labels))
    width = 0.30

    fig, ax = plt.subplots(layout="constrained", figsize=(8, 5))
    ax.bar(x - width / 2, b04_vals, width, label="B04 Red", color="tomato")
    ax.bar(x + width / 2, b08_vals, width, label="B08 NIR", color="steelblue")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Surface Reflectance")
    ax.set_title(f"Spectral Signatures — Solapur — {date_label}")
    ax.legend()
    plt.savefig(out_path, dpi=150)
    plt.clf()
    plt.close()
    print(f"  Saved: {out_path}")


def plot_ndvi_change(ndvi_change: np.ndarray, out_path: str) -> None:
    plt.figure(figsize=(8, 7))
    plt.imshow(ndvi_change, cmap="coolwarm", vmin=-0.5, vmax=0.5)
    plt.colorbar(label="ΔNDVI (March − December)")
    plt.title("NDVI Change Detection — Solapur\n31 Dec 2025 → 16 Mar 2026")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.clf()
    plt.close()
    print(f"  Saved: {out_path}")


def plot_threshold_classification(ndvi_change: np.ndarray, out_path: str) -> np.ndarray:
    """
    Classify ΔNDVI into three classes:
      -1 : vegetation loss  (ΔNDVI < -0.2)
       0 : no change        (-0.2 ≤ ΔNDVI ≤ 0.2)
      +1 : vegetation gain  (ΔNDVI > 0.2)
    """
    classified = np.zeros_like(ndvi_change)
    classified[ndvi_change < -0.2] = -1
    classified[ndvi_change >  0.2] =  1
    classified[np.isnan(ndvi_change)] = np.nan

    cmap = mcolors.ListedColormap(["#d73027", "#ffffbf", "#1a9850"])
    bounds = [-1.5, -0.5, 0.5, 1.5]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(8, 7))
    img = ax.imshow(classified, cmap=cmap, norm=norm)
    cbar = fig.colorbar(img, ax=ax, ticks=[-1, 0, 1])
    cbar.ax.set_yticklabels(["Vegetation loss", "No change", "Vegetation gain"])
    ax.set_title(
        "NDVI Threshold Classification — Solapur\n31 Dec 2025 → 16 Mar 2026\n"
        "Threshold: |ΔNDVI| > 0.2"
    )
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.clf()
    plt.close()
    print(f"  Saved: {out_path}")
    return classified 

def print_stats(label: str, arr: np.ndarray) -> None:
    print(
        f"  {label:30s}  "
        f"min={np.nanmin(arr):.4f}  max={np.nanmax(arr):.4f}  "
        f"mean={np.nanmean(arr):.4f}  NaN={np.isnan(arr).sum():,}"
    )

def save_geotiff(array: np.ndarray, ref_ds: rasterio.DatasetReader, out_path: str) -> None:
    """Save array as a georeferenced single-band GeoTIFF."""
    profile = ref_ds.profile.copy()
    profile.update(driver="GTiff", dtype=rasterio.float32, count=1, compress="lzw")
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(array.astype(rasterio.float32), 1)
    print(f"  Saved: {out_path}")
# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── December 2025 ────────────────────────────────────────────────────────
    print("\n[1/3] Processing December 2025...")
    b04_dec, ds_dec = load_band(band_path(SAFE_DEC, GRANULE_DEC, TILE_ID_DEC, "B04"))
    b08_dec, _      = load_band(band_path(SAFE_DEC, GRANULE_DEC, TILE_ID_DEC, "B08"))
    ndvi_dec = compute_ndvi(b04_dec, b08_dec)

    print_stats("B04 Dec", b04_dec)
    print_stats("B08 Dec", b08_dec)
    print_stats("NDVI Dec", ndvi_dec)

    plot_ndvi_map(ndvi_dec, "31 Dec 2025",
                  os.path.join(OUTPUT_DIR, "ndvi_dec2025.png"))
    plot_band_histogram(b04_dec, b08_dec, "31 Dec 2025",
                        os.path.join(OUTPUT_DIR, "histogram_31dec2025.png"))
    plot_ndvi_histogram(ndvi_dec, "31 Dec 2025",
                        os.path.join(OUTPUT_DIR, "ndvi_histogram_31dec2025.png"))

    print("  Spectral signatures (Dec):")
    sigs_dec = extract_spectral_signatures(b04_dec, b08_dec, ds_dec, SAMPLE_POINTS)
    plot_spectral_signatures(sigs_dec, "31 Dec 2025",
                             os.path.join(OUTPUT_DIR, "spectral_signatures_31dec2025.png"))

    # ── March 2026 ───────────────────────────────────────────────────────────
    print("\n[2/3] Processing March 2026...")
    b04_mar, ds_mar = load_band(band_path(SAFE_MARCH, GRANULE_MARCH, TILE_ID_MARCH, "B04"))
    b08_mar, _      = load_band(band_path(SAFE_MARCH, GRANULE_MARCH, TILE_ID_MARCH, "B08"))
    ndvi_mar = compute_ndvi(b04_mar, b08_mar)

    print_stats("B04 March", b04_mar)
    print_stats("B08 March", b08_mar)
    print_stats("NDVI March", ndvi_mar)

    plot_ndvi_map(ndvi_mar, "16 Mar 2026",
                  os.path.join(OUTPUT_DIR, "ndvi_march2026.png"))
    plot_band_histogram(b04_mar, b08_mar, "16 Mar 2026",
                        os.path.join(OUTPUT_DIR, "histogram_16march2026.png"))
    plot_ndvi_histogram(ndvi_mar, "16 Mar 2026",
                        os.path.join(OUTPUT_DIR, "ndvi_histogram_16march2026.png"))

    print("  Spectral signatures (March):")
    sigs_mar = extract_spectral_signatures(b04_mar, b08_mar, ds_mar, SAMPLE_POINTS)
    plot_spectral_signatures(sigs_mar, "16 Mar 2026",
                             os.path.join(OUTPUT_DIR, "spectral_signatures_16march2026.png"))

    # ── Change Detection ─────────────────────────────────────────────────────
    print("\n[3/3] Computing NDVI change...")

    # Spatial alignment check — raises AssertionError if grids don't match
    assert ds_dec.shape == ds_mar.shape, \
        f"Shape mismatch: Dec {ds_dec.shape} vs Mar {ds_mar.shape}"
    assert ds_dec.transform == ds_mar.transform, \
        "Transform mismatch — rasters are not spatially aligned"
    print("  Spatial alignment confirmed.")

    ndvi_change = ndvi_mar - ndvi_dec
    print_stats("ΔNDVI (March − Dec)", ndvi_change)

    loss_pct = (ndvi_change < -0.2).sum() / np.isfinite(ndvi_change).sum() * 100
    gain_pct = (ndvi_change >  0.2).sum() / np.isfinite(ndvi_change).sum() * 100
    print(f"  Vegetation loss pixels (ΔNDVI < -0.2): {loss_pct:.1f}%")
    print(f"  Vegetation gain pixels (ΔNDVI >  0.2): {gain_pct:.1f}%")

    plot_ndvi_change(ndvi_change,
                     os.path.join(OUTPUT_DIR, "ndvi_change_detection.png"))
    classified = plot_threshold_classification(ndvi_change,
                                  os.path.join(OUTPUT_DIR, "ndvi_threshold_classified.png"))
    save_geotiff(ndvi_change, ds_dec, os.path.join(OUTPUT_DIR, "ndvi_change.tif"))
    save_geotiff(classified,  ds_dec, os.path.join(OUTPUT_DIR, "ndvi_classified.tif"))
    ds_dec.close()
    ds_mar.close()
    print("\nDone. All outputs saved to ./outputs/")


if __name__ == "__main__":
    main()