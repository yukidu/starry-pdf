"""End-to-end HTTP test against local standalone Starry PDF containers.

Creates blank PDFs in memory. No personal documents or authentication data.
"""
import io
import sys
import time
import zipfile

import httpx
from pypdf import PdfReader, PdfWriter

BASE = "http://127.0.0.1:8090"

def pdf(pages: int) -> bytes:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(595, 842)
    out = io.BytesIO()
    writer.write(out)
    writer.close()
    return out.getvalue()

def wait_until_ready():
    for _ in range(90):
        try:
            homepage = httpx.get(BASE + "/", timeout=6)
            health = httpx.get(BASE + "/api/health", timeout=6)
            if homepage.status_code == 200 and "繁星 PDF" in homepage.text and health.json()["status"] == "ok":
                print("Starry PDF UI and API are ready", flush=True)
                return
        except Exception:
            pass
        time.sleep(3)
    raise AssertionError("Independent PDF app did not become healthy")

def require_pdf(response: httpx.Response, expected: int):
    assert response.status_code == 200, (response.status_code, response.text[:200])
    assert response.headers["content-type"].startswith("application/pdf")
    assert len(PdfReader(io.BytesIO(response.content)).pages) == expected

def test_end_to_end():
    with httpx.Client(timeout=60) as client:
        one = pdf(1)
        a = client.post(BASE + "/api/pdf/merge", files=[
            ("files", ("first.pdf", one, "application/pdf")),
            ("files", ("second.pdf", one, "application/pdf")),
        ])
        require_pdf(a, 2)
        print("Independent merge API: OK", flush=True)
        b = client.post(BASE + "/api/pdf/split", data={"pages":"1-2"}, files={"file":("merged.pdf",a.content,"application/pdf")})
        assert b.status_code == 200, (b.status_code,b.text[:200])
        with zipfile.ZipFile(io.BytesIO(b.content)) as z:
            assert len(z.namelist()) == 2
        print("Independent split API: OK", flush=True)
        c = client.post(BASE + "/api/pdf/rotate", data={"degrees":"90"},files={"file":("x.pdf",a.content,"application/pdf")})
        require_pdf(c, 2)
        print("Independent rotate API: OK", flush=True)
        d = client.post(BASE + "/api/pdf/optimize",files={"file":("x.pdf",a.content,"application/pdf")})
        require_pdf(d, 2)
        print("Independent optimize API: OK", flush=True)
        pwa = client.get(BASE + "/manifest.webmanifest")
        assert pwa.status_code == 200 and pwa.json()["display"] == "standalone"
        print("PWA manifest: OK", flush=True)

if __name__ == "__main__":
    try:
        wait_until_ready()
        test_end_to_end()
        print("Independent open-source PDF app HTTP smoke: PASS")
    except Exception as exc:
        print(f"FAIL: {exc}",file=sys.stderr)
        sys.exit(1)
