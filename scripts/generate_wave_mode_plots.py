from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


FREQUENCIES = [170, 255, 343, 425, 510, 680]
SOUND_SPEED = 343.0
TUBE_LENGTH_CM = 50.0
MEASURED_MAX_CM = 43.0
PLOT_MAX_CM = TUBE_LENGTH_CM

REFERENCE_LABELS = {
    170: "open-closed reference: fundamental quarter-wave pressure guide",
    255: "intermediate mapping frequency: between 170 and 343 Hz references",
    343: "closed-closed/open-open reference: first half-wave pressure guide",
    425: "intermediate mapping frequency: between 343 and 510 Hz references",
    510: "open-closed reference: third-quarter-wave pressure guide",
    680: "closed-closed/open-open reference: second half-wave pressure guide",
}

COLORS = {
    170: "#2563eb",
    255: "#0f766e",
    343: "#f97316",
    425: "#8b5cf6",
    510: "#ef4444",
    680: "#0891b2",
}


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, Path]:
    project_root = Path(__file__).resolve().parents[1]
    analysis_dir = project_root / "data" / "mode_shape"
    summary = pd.read_csv(analysis_dir / "mode_shape_6freq_filled_normalized_summary.csv")
    params = pd.read_csv(analysis_dir / "ideal_reference_fit_parameters.csv")
    return summary, params, project_root


def fitted_pressure_envelope(x_cm: np.ndarray, freq_hz: int, params: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    row = params.loc[params["frequency_Hz"] == freq_hz].iloc[0]
    x_m = x_cm / 100.0
    phase = float(row["phase_rad"])
    signed_pressure = np.cos(2 * np.pi * freq_hz / SOUND_SPEED * x_m + phase)
    pressure_envelope = float(row["offset_a"]) + float(row["scale_b"]) * np.abs(signed_pressure)
    pressure_envelope = np.clip(pressure_envelope, 0.0, 1.05)
    particle_motion = np.sin(2 * np.pi * freq_hz / SOUND_SPEED * x_m + phase)
    return pressure_envelope, signed_pressure, particle_motion


def reference_wave_guides(x_cm: np.ndarray, freq_hz: int) -> tuple[np.ndarray, np.ndarray]:
    """Return ideal signed pressure and complementary particle-motion guides.

    The lower strip is an interpretation guide, so principal reference
    frequencies use the textbook 50 cm tube mode family rather than fitted
    phase from the measured RMS envelope.
    """
    xi = x_cm / TUBE_LENGTH_CM
    if freq_hz == 170:
        signed_pressure = np.sin(0.5 * np.pi * xi)
        particle_motion = np.cos(0.5 * np.pi * xi)
    elif freq_hz == 510:
        signed_pressure = np.sin(1.5 * np.pi * xi)
        particle_motion = np.cos(1.5 * np.pi * xi)
    elif freq_hz == 343:
        signed_pressure = np.cos(np.pi * xi)
        particle_motion = np.sin(np.pi * xi)
    elif freq_hz == 680:
        signed_pressure = np.cos(2.0 * np.pi * xi)
        particle_motion = np.sin(2.0 * np.pi * xi)
    else:
        # Intermediate mapping frequencies are visual guides only; use the
        # actual drive wavenumber with an open-end-like pressure node reference.
        x_m = x_cm / 100.0
        signed_pressure = np.sin(2 * np.pi * freq_hz / SOUND_SPEED * x_m)
        particle_motion = np.cos(2 * np.pi * freq_hz / SOUND_SPEED * x_m)
    return signed_pressure, particle_motion


def load_raw_points(freq_df: pd.DataFrame, project_root: Path, freq_hz: int) -> tuple[list[np.ndarray], list[float], list[float]]:
    raw_values: list[np.ndarray] = []
    raw_positions: list[float] = []
    med_max = float(freq_df["median_amp"].max())
    for _, row in freq_df.iterrows():
        if bool(row["is_estimated"]) or not isinstance(row["raw_csv"], str) or not row["raw_csv"]:
            continue
        raw_name = Path(str(row["raw_csv"]).replace("\\", "/")).name
        raw_path = project_root / "data" / "mode_shape" / "raw" / raw_name
        if not raw_path.exists():
            continue
        raw = pd.read_csv(raw_path)
        vals = raw["amplitude"].to_numpy(dtype=float) / med_max
        raw_values.append(vals)
        raw_positions.append(float(row["position_cm"]))
    return raw_values, raw_positions, [p + 0.35 for p in raw_positions]


def make_plot(freq_hz: int, summary: pd.DataFrame, params: pd.DataFrame, project_root: Path, out_dir: Path) -> None:
    freq_df = summary.loc[summary["frequency_Hz"] == freq_hz].sort_values("position_cm").copy()
    x = freq_df["position_cm"].to_numpy(dtype=float)
    y = freq_df["norm_median"].to_numpy(dtype=float)
    yerr = freq_df["norm_std"].to_numpy(dtype=float)
    estimated = freq_df["is_estimated"].astype(bool).to_numpy()

    raw_values, raw_positions, box_positions = load_raw_points(freq_df, project_root, freq_hz)
    x_dense = np.linspace(0, PLOT_MAX_CM, 700)
    ideal_env, _, _ = fitted_pressure_envelope(x_dense, freq_hz, params)
    signed_pressure, particle_motion = reference_wave_guides(x_dense, freq_hz)

    color = COLORS[freq_hz]
    fig = plt.figure(figsize=(11.5, 7.0), dpi=180, layout="constrained")
    gs = fig.add_gridspec(2, 1, height_ratios=[3.0, 1.05], hspace=0.25)
    ax = fig.add_subplot(gs[0, 0])
    ax_wave = fig.add_subplot(gs[1, 0], sharex=ax)

    if raw_values:
        bp = ax.boxplot(
            raw_values,
            positions=box_positions,
            widths=0.28,
            patch_artist=True,
            showfliers=False,
            manage_ticks=False,
        )
        for patch in bp["boxes"]:
            patch.set(facecolor=color, alpha=0.14, edgecolor=color, linewidth=0.8)
        for key in ["whiskers", "caps", "medians"]:
            for line in bp[key]:
                line.set(color=color, linewidth=0.8, alpha=0.8)

    for px, vals in zip(raw_positions, raw_values):
        if len(vals) == 0:
            continue
        jitter = np.linspace(-0.16, 0.16, len(vals)) if len(vals) > 1 else np.array([0.0])
        ax.scatter(
            px + jitter,
            vals,
            s=8,
            color=color,
            alpha=0.25,
            linewidths=0,
            label="_raw",
        )

    ax.plot(x_dense, ideal_env, color="#111827", linestyle="--", linewidth=2.0, label="Ideal pressure envelope")
    ax.plot(x, y, color=color, linewidth=2.4, marker="o", markersize=4.0, label="Measured pressure RMS envelope")
    ax.fill_between(x, np.maximum(0, y - yerr), np.minimum(1.08, y + yerr), color=color, alpha=0.12, linewidth=0)

    if estimated.any():
        ax.scatter(
            x[estimated],
            y[estimated],
            s=40,
            facecolors="white",
            edgecolors=color,
            marker="D",
            linewidths=1.4,
            label="Filled point",
            zorder=5,
        )

    ax.set_title(f"{freq_hz} Hz mode-shape map: measured RMS, ideal pressure envelope and wave guide", fontsize=13, weight="bold")
    ax.set_ylabel("Normalized relative RMS amplitude", fontsize=11)
    ax.set_xlim(0, PLOT_MAX_CM)
    ax.set_ylim(-0.03, 1.12)
    ax.set_xticks(np.arange(0, PLOT_MAX_CM + 1, 5))
    ax.grid(True, alpha=0.22, linewidth=0.7)
    ax.text(
        0.01,
        0.96,
        REFERENCE_LABELS[freq_hz],
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=9.2,
        color="#374151",
        bbox=dict(facecolor="white", edgecolor="#d1d5db", boxstyle="round,pad=0.25", alpha=0.92),
    )
    ax.legend(loc="lower right", fontsize=8.4, frameon=True, framealpha=0.92, borderpad=0.45)

    ax_wave.axhline(0, color="#9ca3af", linewidth=0.8)
    ax_wave.plot(x_dense, signed_pressure, color="#1d4ed8", linewidth=1.8, label="Reference signed pressure wave")
    ax_wave.plot(x_dense, particle_motion, color="#dc2626", linewidth=1.6, linestyle=":", label="Particle-motion guide")
    ax_wave.fill_between(x_dense, 0, signed_pressure, color="#1d4ed8", alpha=0.07)
    ax_wave.set_ylabel("Wave guide", fontsize=10)
    ax_wave.set_xlabel("Microphone position along tube / cm", fontsize=11)
    ax_wave.set_ylim(-1.25, 1.25)
    ax_wave.set_yticks([-1, 0, 1])
    ax_wave.grid(True, axis="x", alpha=0.18, linewidth=0.6)
    ax_wave.legend(loc="upper right", fontsize=8.4, frameon=True, ncol=2, framealpha=0.92)
    out_path = out_dir / f"mode_shape_{freq_hz}Hz_wave.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(out_path)


def main() -> None:
    summary, params, project_root = load_data()
    out_dir = project_root / "figures"
    out_dir.mkdir(exist_ok=True)
    for freq in FREQUENCIES:
        make_plot(freq, summary, params, project_root, out_dir)


if __name__ == "__main__":
    main()
