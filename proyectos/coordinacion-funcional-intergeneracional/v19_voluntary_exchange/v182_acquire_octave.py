"""Acquire a project-local portable Octave from the official GNU distribution.

No installer, PATH change, registry change, or administrator privileges.
The recorded SHA256 identifies acquired bytes; it is not a signature check.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
import urllib.request

ROOT = Path(r"C:\Programación\tools\octave-11.3.0")
URL = "https://ftp.gnu.org/gnu/octave/windows/octave-11.3.0-w64.7z"


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    archive = ROOT / "octave-11.3.0-w64.7z"
    started = time.monotonic()
    if not archive.exists():
        part = archive.with_suffix(".7z.part")
        if part.exists():
            raise FileExistsError(f"Inspect existing partial acquisition: {part}")
        h = hashlib.sha256()
        count = 0
        with urllib.request.urlopen(URL, timeout=90) as response, part.open("xb") as out:
            expected = response.headers.get("Content-Length")
            final_url = response.url
            while block := response.read(4 * 1024 * 1024):
                out.write(block)
                h.update(block)
                count += len(block)
                if count % (32 * 1024 * 1024) == 0:
                    print("OCTAVE_DOWNLOAD", count, round(time.monotonic()-started, 1), flush=True)
        if expected is not None:
            assert count == int(expected), (count, expected)
        part.rename(archive)
        (ROOT / "ACQUISITION.json").write_text(json.dumps(dict(
            url=URL, final_url=final_url, bytes=count, sha256=h.hexdigest(),
            detached_signature_verified=False, installer_executed=False,
        ), indent=2), encoding="utf-8")
    extracted = ROOT / "portable"
    if extracted.exists():
        raise FileExistsError(f"Do not overwrite existing portable installation: {extracted}")
    flags = (subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS) if os.name == 'nt' else 0
    listing = subprocess.check_output(["tar", "-tf", str(archive)], text=True, creationflags=flags)
    for member in listing.splitlines():
        p = Path(member)
        assert not p.is_absolute() and ".." not in p.parts and ":" not in member, member
    extracted.mkdir()
    subprocess.run(["tar", "-xf", str(archive), "-C", str(extracted)], check=True, creationflags=flags)
    executables = list(extracted.rglob("octave-cli.exe"))
    assert len(executables) == 1, executables
    print("OCTAVE_READY", str(executables[0]), "elapsed", round(time.monotonic()-started, 1), flush=True)


if __name__ == "__main__":
    main()
