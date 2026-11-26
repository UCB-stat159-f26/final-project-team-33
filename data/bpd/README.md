# Berkeley Police Department data

The `raw/` folder contains the stop, calls for service, and collision CSV exports downloaded from the Berkeley Police Transparency Hub on November 26, 2026. Each file preserves the rows, column names, and values of one published release. The date ranges below follow the publisher’s titles. [Berkeley Police Transparency Hub](https://bpd-transparency-initiative-berkeleypd.hub.arcgis.com/search)

| Published release | Local file | Source |
| --- | --- | --- |
| Stops, January 26, 2015 through September 30, 2020 | `raw/stops_2015_2020.csv` | [BPD release](https://bpd-transparency-initiative-berkeleypd.hub.arcgis.com/datasets/3c9b2272178549698b3fde550ca33ba9/about) |
| Stops, October 1, 2020 through December 31, 2023 | `raw/stops_2020_2023.csv` | [BPD release](https://bpd-transparency-initiative-berkeleypd.hub.arcgis.com/datasets/35cc0ccb17ba400b93cba5db5a37b140/about) |
| Stops, 2024 onward | `raw/stops_2024_onward.csv` | [BPD release](https://bpd-transparency-initiative-berkeleypd.hub.arcgis.com/datasets/078f7d987228453ca30cf7a99311d8de/about) |
| Calls for service, 2016 to 2021 | `raw/calls_for_service_2016_2021.csv.gz` | [BPD release](https://bpd-transparency-initiative-berkeleypd.hub.arcgis.com/datasets/59b2211c4f19499f9bb86ccd2023f87b/about) |
| Calls for service, current layer (`callsforservice_csv`) | `raw/calls_for_service_current.csv.gz` | [BPD release](https://bpd-transparency-initiative-berkeleypd.hub.arcgis.com/datasets/3be134af40954e19a3d308779a65f175/about) |
| Collisions, 2011 onward | `raw/collisions.csv` | [BPD release](https://bpd-transparency-initiative-berkeleypd.hub.arcgis.com/datasets/fcb1720b81844fed9d2212ffe2f35c74/about) |

Both calls-for-service releases contain records dated 2021. The files are stored separately because their coverage overlaps and their column names differ.

The two calls files use gzip compression to reduce their size in Git. Python’s `pandas.read_csv()` accepts their `.csv.gz` paths directly. In R, use `read.csv(gzfile(path))`.

## Verify the files

Run this command from the repository root. It uses the Python standard library and works offline.

```bash
python3 scripts/bpd_data.py
```

Each checksum covers the original CSV bytes, after decompression for the two calls files. The source table records the SHA-256 checksum, direct download link, retrieval date, and number of data rows for each release. [Source table](sources.csv)

## Download from Berkeley

To fetch the public exports again, choose a new or empty directory for the downloads.

```bash
python3 scripts/bpd_data.py --download-to downloads/bpd
```

Berkeley can update its exports. The command reports whether each download matches the recorded snapshot.
