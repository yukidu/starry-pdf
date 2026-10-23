"""Independently verify real PDF operations, without user files."""
import io
import zipfile
from fastapi.testclient import TestClient
from pypdf import PdfReader, PdfWriter
from api.main import app
client = TestClient(app)

def sample(pages=2):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(595, 842)
    stream = io.BytesIO()
    writer.write(stream)
    writer.close()
    return stream.getvalue()

def test_health():
    assert client.get("/api/health").json()["status"] == "ok"

def test_merge():
    r = client.post("/api/pdf/merge", files=[
        ("files", ("a.pdf", sample(2), "application/pdf")),
        ("files", ("b.pdf", sample(3), "application/pdf"))])
    assert r.status_code == 200, r.text
    assert len(PdfReader(io.BytesIO(r.content)).pages) == 5
    assert r.headers["cache-control"] == "no-store"

def test_split_pages():
    r = client.post("/api/pdf/split", data={"pages": "1-2,4"},
        files={"file": ("a.pdf", sample(4), "application/pdf")})
    assert r.status_code == 200, r.text
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        assert z.namelist() == ["page-001.pdf", "page-002.pdf", "page-004.pdf"]
        assert all(len(PdfReader(io.BytesIO(z.read(n))).pages) == 1 for n in z.namelist())

def test_rotate():
    r = client.post("/api/pdf/rotate", data={"degrees": "90"},
        files={"file": ("a.pdf", sample(), "application/pdf")})
    assert r.status_code == 200, r.text
    assert all(p.get("/Rotate") == 90 for p in PdfReader(io.BytesIO(r.content)).pages)

def test_optimize():
    r = client.post("/api/pdf/optimize",
        files={"file": ("a.pdf", sample(), "application/pdf")})
    assert r.status_code == 200, r.text
    assert len(PdfReader(io.BytesIO(r.content)).pages) == 2

def test_bad_extension():
    r = client.post("/api/pdf/optimize",
        files={"file": ("a.txt", b"bad", "text/plain")})
    assert r.status_code == 422

def test_bad_contents():
    r = client.post("/api/pdf/optimize",
        files={"file": ("a.pdf", b"not a pdf", "application/pdf")})
    assert r.status_code == 422

def test_too_large():
    r = client.post("/api/pdf/optimize",
        files={"file": ("a.pdf", b"%PDF-1.4" + b"x" * (12*1024*1024), "application/pdf")})
    assert r.status_code == 413

def test_encrypted():
    w = PdfWriter()
    w.add_blank_page(595, 842)
    w.encrypt("test-password")
    stream = io.BytesIO()
    w.write(stream)
    r = client.post("/api/pdf/rotate", data={"degrees": "90"},
        files={"file": ("a.pdf", stream.getvalue(), "application/pdf")})
    assert r.status_code == 422

def test_invalid_rotation():
    r = client.post("/api/pdf/rotate", data={"degrees": "45"},
        files={"file": ("a.pdf", sample(), "application/pdf")})
    assert r.status_code == 422

def test_invalid_pages():
    for pages in ["0", "3", "2-1", "1,1", "1,,2", "a", "1-"]:
        r = client.post("/api/pdf/split", data={"pages": pages},
            files={"file": ("a.pdf", sample(), "application/pdf")})
        assert r.status_code == 422, (pages, r.status_code)

def test_file_limit():
    r = client.post("/api/pdf/merge",
        files=[("files", (f"{i}.pdf", sample(1), "application/pdf")) for i in range(7)])
    assert r.status_code == 422
