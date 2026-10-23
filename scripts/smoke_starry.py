"""End-to-end HTTP test for standalone local Starry PDF containers, no user data."""
import io
import sys
import time
import zipfile
import httpx
from pypdf import PdfReader, PdfWriter

BASE = "http://127.0.0.1:8090"

def sample(pages: int) -> bytes:
    w = PdfWriter()
    for _ in range(pages):
        w.add_blank_page(595, 842)
    out = io.BytesIO()
    w.write(out)
    w.close()
    return out.getvalue()

def wait_until_ready() -> None:
    last = ""
    for n in range(30):
        try:
            homepage = httpx.get(BASE + "/", timeout=5)
            health = httpx.get(BASE + "/api/health", timeout=5)
            last = f"home={homepage.status_code} api={health.status_code}"
            if homepage.status_code == 200 and "繁星 PDF" in homepage.text and health.status_code == 200 and health.json()["status"] == "ok":
                print("Starry PDF website and API: READY", flush=True)
                return
        except Exception as exc:
            last = str(exc)[:160]
        if n % 5 == 0:
            print(f"Waiting for local website: {last}", flush=True)
        time.sleep(2)
    raise AssertionError(f"Standalone PDF site did not become healthy: {last}")

def assert_pdf(response: httpx.Response, pages: int):
    assert response.status_code == 200, (response.status_code, response.text[:220])
    assert response.headers["content-type"].startswith("application/pdf")
    assert len(PdfReader(io.BytesIO(response.content)).pages) == pages

def verify_http() -> None:
    with httpx.Client(timeout=60) as client:
        a = sample(1)
        merged = client.post(BASE + "/api/pdf/merge", files=[
            ("files", ("first.pdf", a, "application/pdf")),
            ("files", ("second.pdf", a, "application/pdf")),
        ])
        assert_pdf(merged, 2)
        print("Merged two PDF files: OK", flush=True)
        split = client.post(BASE + "/api/pdf/split", data={"pages": "1-2"},
            files={"file": ("merged.pdf", merged.content, "application/pdf")})
        assert split.status_code == 200, (split.status_code, split.text[:200])
        with zipfile.ZipFile(io.BytesIO(split.content)) as z:
            assert len(z.namelist()) == 2
        print("Split into two PDF files: OK", flush=True)
        rotate = client.post(BASE + "/api/pdf/rotate", data={"degrees": "90"},
            files={"file": ("merged.pdf", merged.content, "application/pdf")})
        assert_pdf(rotate, 2)
        print("Rotated PDF: OK", flush=True)
        optimize = client.post(BASE + "/api/pdf/optimize",
            files={"file": ("merged.pdf", merged.content, "application/pdf")})
        assert_pdf(optimize, 2)
        print("Optimized PDF: OK", flush=True)
        manifest = client.get(BASE + "/manifest.webmanifest")
        assert manifest.status_code == 200 and manifest.json()["display"] == "standalone"
        print("PWA manifest: OK", flush=True)
        app_bundle = client.get(BASE + "/index.html")
        assert app_bundle.status_code == 200 and 'id="root"' in app_bundle.text
        print("React entrypoint: OK", flush=True)

if __name__ == "__main__":
    try:
        wait_until_ready()
        verify_http()
        print("INDEPENDENT STARRY PDF END-TO-END: PASS", flush=True)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr, flush=True)
        sys.exit(1)
