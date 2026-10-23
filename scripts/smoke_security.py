#!/usr/bin/env python3
"""Confirm the normal local instance rejects unauthenticated PDF operations.

This check intentionally uses generated blank test files and no credentials.
"""
from __future__ import annotations

import io
import sys
import time

import requests
from pypdf import PdfWriter

BASE = "http://127.0.0.1:8088"


def sample_pdf() -> bytes:
    doc = PdfWriter()
    doc.add_blank_page(width=595, height=842)
    buffer = io.BytesIO()
    doc.write(buffer)
    return buffer.getvalue()


def wait_for_up(seconds: int = 390) -> None:
    last = "not running"
    start = time.monotonic()
    while time.monotonic() - start < seconds:
        try:
            response = requests.get(BASE + "/api/v1/info/status", timeout=10)
            if response.status_code == 200:
                print("Protected PDF instance started successfully", flush=True)
                return
            last = str(response.status_code)
        except requests.RequestException as exc:
            last = str(exc)
        time.sleep(5)
    raise RuntimeError(f"Protected PDF instance did not become healthy: {last}")


def check_login_guard() -> None:
    source = sample_pdf()
    resp = requests.post(
        BASE + "/api/v1/general/merge-pdfs",
        files=[
            ("fileInput", ("a.pdf", io.BytesIO(source), "application/pdf")),
            ("fileInput", ("b.pdf", io.BytesIO(source), "application/pdf")),
        ],
        data={"sortType": "byFileName"},
        timeout=45,
        allow_redirects=False,
    )
    code = resp.status_code
    location = resp.headers.get("Location", "").lower()
    if code not in (401, 403) and not (300 <= code < 400 and "login" in location):
        raise AssertionError(
            f"Protected PDF API unexpectedly accessible: status={code}, "
            f"location={location[:100]}, type={resp.headers.get('Content-Type')}"
        )
    print(f"Unauthenticated PDF processing correctly blocked (HTTP {code})", flush=True)


if __name__ == "__main__":
    try:
        wait_for_up()
        check_login_guard()
    except Exception as exc:
        print(f"SECURITY SMOKE FAILED: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)
