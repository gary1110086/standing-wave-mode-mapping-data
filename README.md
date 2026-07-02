# Standing-Wave Mode Mapping Data Package

This repository contains the data files, figure files, and calculation scripts used for the undergraduate lab report:

**Standing-Wave Mode Mapping in a Loudspeaker-Driven Tube**

## Measurement Note

The measured quantity is relative microphone RMS amplitude. It is used as a relative pressure-amplitude indicator. It is not calibrated SPL and it is not absolute pressure in Pa.

The report uses the sensor name **KY-037** or **microphone sound detection sensor**.

## Repository Contents

- `data/mode_shape/mode_shape_6freq_normalized_summary.csv`  
  Main frequency-position mapping table for 170 Hz, 255 Hz, 343 Hz, 425 Hz, 510 Hz, and 680 Hz.

- `data/mode_shape/mode_shape_6freq_row_normalized_heatmap_table.csv`  
  Row-normalized table used for the six-frequency heatmap.

- `data/mode_shape/ideal_reference_fit_parameters.csv`  
  Parameters used for the ideal reference envelope guides.

- `data/mode_shape/raw/`  
  Microphone capture CSV files used for the position-mapping analysis.

- `data/frequency_sweep/frequency_response_summary.csv`  
  Fixed-position frequency sweep data near x = 37.5 cm.

- `figures/`  
  Report figures, including apparatus photos, sweep plot, heatmap, mode-shape plots, and bead visualization figures.

- `figures/raw_beads/`  
  Bead photos used by `scripts/generate_beads_wave_guides.py`.

- `scripts/generate_wave_mode_plots.py`  
  Creates the six mode-shape guide plots from the CSV files in `data/mode_shape/`.

- `scripts/generate_beads_wave_guides.py`  
  Creates the bead visualization guide figures from `figures/raw_beads/`.

- `report/main.tex` and `report/figures/`  
  Portable LaTeX report source and figures. This folder can be uploaded to Overleaf as a self-contained report package.

## Creating Figures

From the repository root:

```powershell
python .\scripts\generate_wave_mode_plots.py
python .\scripts\generate_beads_wave_guides.py
```

The scripts write figures to `figures/`.

## Compiling the Report

From the repository root:

```powershell
cd .\report
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
```

The report figures are stored in `report/figures/`, so the LaTeX source should also compile after uploading the `report/` folder to Overleaf.
