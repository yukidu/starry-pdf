#!/usr/bin/env python3
"""Integration tests of actual PDF processing in a disposable local CI container.

The sample PDFs are generated here and contain no real user data.
This is an evaluation-only test of the separately licensed official image;
it is NOT approval to deploy the image to production.
"""
from __future__ import annotations

import io
import sys
import time
import zipfile

import requests
from pypdf import PdfReader, PdfWriter

BASE_URL = "http://127.0.0.1:8088"


def wait_for_backend(seconds: int = 390) -> None:
    start = time.monotonic()
    last_error = "not started"
    while time.monotonic() - start < seconds:
        try:
            r = requests.get(f"{BASE_URL}/", timeout=12, allow_redirects=True)
            if r.status_code == 200 and "<html" in r.text.lower():
                print("PDF service web interface is ready", flush=True)
                return
            last_error = f"status={r.status_code}, body={r.text[:160]}"
        except requests.RequestException as exc:
            last_error = str(exc)
        time.sleep(5)
    raise RuntimeError(f"PDF backend did not start within {seconds}s: {last_error}")


def check_pwa_entry() -> None:
    response = requests.get(f"{BASE_URL}/install", timeout=12)
    response.raise_for_status()
    assert "繁星 PDF" in response.text, "PWA entry missing"
    manifest = requests.get(f"{BASE_URL}/manifest.webmanifest", timeout=12)
    manifest.raise_for_status()
    assert manifest.json()["start_url"] == "/install"
    print("PWA installation entry HTTP smoke passed", flush=True)


def blank_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()


def process(path: str, files: list[tuple[str, str, bytes]], data: dict[str, str]) -> requests.Response:
    body = [
        (field, (filename, io.BytesIO(content), "application/pdf"))
        for field, filename, content in files
    ]
    response = requests.post(
        f"{BASE_URL}{path}", files=body, data=data, timeout=180
    )
    if response.status_code != 200:
        raise AssertionError(
            f"{path}: expected 200, got {response.status_code}; "
            f"content type={response.headers.get('content-type')}; "
            f"response={response.text[:500]}"
        )
    return response


def assert_pdf(raw: bytes, expected_pages: int) -> None:
    assert raw.startswith(b"%PDF-"), "Expected a PDF response"
    actual = len(PdfReader(io.BytesIO(raw)).pages)
    assert actual == expected_pages, f"Expected {expected_pages} pages, got {actual}"


def test_pdf_engine() -> None:
    original = blank_pdf()
    merged = process(
        "/api/v1/general/merge-pdfs",
        [
            ("fileInput", "a.pdf", original),
            ("fileInput", "b.pdf", original),
        ],
        {"sortType": "byFileName"},
    )
    assert_pdf(merged.content, 2)
    print("ACTUAL PDF merge: passed (2 pages)", flush=True)

    split = process(
        "/api/v1/general/split-pages",
        [("fileInput", "merged.pdf", merged.content)],
        {"pageNumbers": "all"},
    )
    with zipfile.ZipFile(io.BytesIO(split.content)) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".pdf")]
        assert len(names) == 2, f"Expected 2 split files, got {names}"
        for name in names:
            assert_pdf(archive.read(name), 1)
    print("ACTUAL PDF split: passed (2 separate single-page files)", flush=True)

    compressed = process(
        "/api/v1/misc/compress-pdf",
        [("fileInput", "merged.pdf", merged.content)],
        {"optimizeLevel": "4"},
    )
    assert_pdf(compressed.content, 2)
    print("ACTUAL PDF compression: passed (valid 2-page PDF)", flush=True)


if __name__ == "__main__":
    try:
        check_pwa_entry()
        wait_for_backend()
        test_pdf_engine()
        print("Docker PDF smoke suite completed successfully", flush=True)
    except Exception as exc:
        print(f"PDF runtime smoke FAILED: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)
