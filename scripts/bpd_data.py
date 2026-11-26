"""Verify or download public CSV releases from the Berkeley Police Department."""

import argparse
import csv
import gzip
import hashlib
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from time import sleep
from typing import BinaryIO
from urllib.parse import urljoin
from urllib.request import urlopen


DATA = Path(__file__).resolve().parents[1] / "data" / "bpd"


def csv_digest(path: Path) -> str:
    """Return the SHA-256 digest of the original CSV bytes in a plain or gzip file."""
    opener = gzip.open if path.suffix == ".gz" else open
    digest = hashlib.sha256()
    with opener(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_csv(url: str, output: BinaryIO) -> None:
    """Copy a public CSV export to an open binary stream, waiting for ArcGIS if needed."""
    for _ in range(60):
        with urlopen(url, timeout=120) as response:
            first = response.readline(65536)
            if response.status == 202 or first.lstrip().startswith(b"{"):
                job = json.loads(first + response.read()) if first.strip() else {"status": "Pending"}
            else:
                if not first or first.lstrip().startswith(b"<") or b"," not in first:
                    raise ValueError(f"Expected a CSV header from {url}")
                output.write(first)
                shutil.copyfileobj(response, output)
                length = response.headers.get("Content-Length")
                if length is not None and output.tell() != int(length):
                    raise OSError(f"Incomplete CSV download from {url}")
                return
        status = str(job.get("status", "")).lower().replace(" ", "")
        if status in {"complete", "completed", "succeeded"} and job.get("resultUrl"):
            url = urljoin(url, job["resultUrl"])
        elif status in {"pending", "processing", "inprogress"}:
            sleep(5)
        else:
            raise RuntimeError(f"ArcGIS export failed: {job.get('message', status)}")
    raise TimeoutError(f"ArcGIS is still preparing {url}. Try again later.")


def download_releases(sources: list, destination: Path) -> None:
    """Save all catalogued releases in a new or empty directory, preserving CSV bytes."""
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError(f"Choose a new or empty download directory: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=destination.parent) as temp:
        staged = Path(temp) / "exports"
        staged.mkdir()
        for source in sources:
            path = staged / source["filename"]
            with path.open("wb") as file:
                if path.suffix == ".gz":
                    with gzip.GzipFile(
                        filename="", mode="wb", fileobj=file, mtime=0, compresslevel=6
                    ) as output:
                        fetch_csv(source["download_url"], output)
                else:
                    fetch_csv(source["download_url"], file)
            matches = csv_digest(path) == source["sha256_csv"]
            status = "matches snapshot" if matches else "differs from snapshot"
            print(f"{path.name}: {status}")
        if destination.is_dir():
            destination.rmdir()
        staged.replace(destination)


def main() -> None:
    """Verify the bundled snapshot or download the releases to a separate directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-to", type=Path, metavar="DIR", help="fetch all releases into DIR")
    args = parser.parse_args()
    with (DATA / "sources.csv").open(encoding="utf-8", newline="") as file:
        sources = list(csv.DictReader(file))
    if args.download_to is not None:
        download_releases(sources, args.download_to)
        return
    for source in sources:
        path = DATA / "raw" / source["filename"]
        if csv_digest(path) != source["sha256_csv"]:
            raise ValueError(f"CSV checksum differs for {path.name}")
        print(f"{path.name}: OK")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        raise SystemExit(str(error))
