"""Independent Starry PDF processing API based on BSD-licensed pypdf.

Local evaluation only; require authentication gateway before any public deploy.
Documents are processed in memory and not persisted.
"""
from __future__ import annotations
import io
import re
import zipfile
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

app = FastAPI(title="Starry PDF Engine", version="0.2.0", docs_url=None, redoc_url=None)
MAX_FILE_BYTES = 12 * 1024 * 1024
MAX_FILES = 6
MAX_TOTAL_PAGES = 400
MAX_OUTPUT_BYTES = 80 * 1024 * 1024

def api_error(status: int, detail: str) -> HTTPException:
    return HTTPException(status_code=status, detail=detail)

async def load_pdf(upload: UploadFile) -> PdfReader:
    try:
        if not upload.filename or not upload.filename.lower().endswith(".pdf"):
            raise api_error(422, "只支援 .pdf 檔案")
        raw = await upload.read(MAX_FILE_BYTES + 1)
        if len(raw) > MAX_FILE_BYTES:
            raise api_error(413, "單一檔案不可超過 12 MB")
        if not raw.lstrip()[:8].startswith(b"%PDF-"):
            raise api_error(422, "檔案不是有效的 PDF")
        try:
            pdf = PdfReader(io.BytesIO(raw), strict=False)
            if pdf.is_encrypted:
                raise api_error(422, "請先使用原密碼解除 PDF 加密")
            pages = len(pdf.pages)
        except HTTPException:
            raise
        except (PdfReadError, ValueError, KeyError, TypeError, OSError, IndexError) as exc:
            raise api_error(422, "PDF 已損壞或不支援") from exc
        if pages < 1 or pages > MAX_TOTAL_PAGES:
            raise api_error(422, "PDF 頁數需介於 1～400 頁")
        return pdf
    finally:
        await upload.close()

def render(writer: PdfWriter, filename: str) -> Response:
    out = io.BytesIO()
    try:
        writer.write(out)
    except (PdfReadError, ValueError, TypeError, OSError, KeyError, IndexError) as exc:
        raise api_error(422, "無法產生 PDF，請確認原檔案") from exc
    data = out.getvalue()
    if len(data) > MAX_OUTPUT_BYTES:
        raise api_error(413, "產生的檔案超過大小限制")
    return Response(content=data, media_type="application/pdf", headers={
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

def check_page_budget(pdfs: list[PdfReader]) -> None:
    if sum(len(pdf.pages) for pdf in pdfs) > MAX_TOTAL_PAGES:
        raise api_error(422, "一次最多處理 400 頁")

def selected_pages(spec: str, count: int) -> list[int]:
    if len(spec) > 240 or not re.fullmatch(r"[0-9,\-\s]+", spec):
        raise api_error(422, "頁碼格式錯誤，例如 1-3,5")
    result: list[int] = []
    used: set[int] = set()
    for segment in spec.split(","):
        piece = segment.strip()
        if not piece:
            raise api_error(422, "頁碼不可為空白")
        parts = piece.split("-")
        if len(parts) == 1:
            pages = [int(parts[0])]
        elif len(parts) == 2 and all(p.strip().isdigit() for p in parts):
            start, end = (int(p) for p in parts)
            if start > end or end - start > MAX_TOTAL_PAGES:
                raise api_error(422, "頁碼範圍錯誤或太大")
            pages = list(range(start, end + 1))
        else:
            raise api_error(422, "頁碼格式錯誤")
        for n in pages:
            if n < 1 or n > count:
                raise api_error(422, "指定的頁碼不存在")
            if n in used:
                raise api_error(422, "請勿重複選擇頁碼")
            used.add(n)
            result.append(n - 1)
    return result

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "starry-pdf-engine"}

@app.post("/api/pdf/merge")
async def merge(files: Annotated[list[UploadFile], File()]) -> Response:
    if len(files) < 2 or len(files) > MAX_FILES:
        raise api_error(422, "請選擇 2～6 個 PDF")
    pdfs = [await load_pdf(f) for f in files]
    check_page_budget(pdfs)
    writer = PdfWriter()
    try:
        for pdf in pdfs:
            writer.append(pdf, import_outline=False)
        return render(writer, "starry-merged.pdf")
    finally:
        writer.close()

@app.post("/api/pdf/split")
async def split(file: Annotated[UploadFile, File()], pages: Annotated[str, Form()]) -> Response:
    pdf = await load_pdf(file)
    numbers = selected_pages(pages, len(pdf.pages))
    result = io.BytesIO()
    with zipfile.ZipFile(result, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for page_index in numbers:
            writer = PdfWriter()
            try:
                writer.add_page(pdf.pages[page_index])
                out = io.BytesIO()
                writer.write(out)
                archive.writestr(f"page-{page_index + 1:03d}.pdf", out.getvalue())
            finally:
                writer.close()
            if result.tell() > MAX_OUTPUT_BYTES:
                raise api_error(413, "輸出檔案太大")
    if len(result.getvalue()) > MAX_OUTPUT_BYTES:
        raise api_error(413, "輸出檔案太大")
    return Response(result.getvalue(), media_type="application/zip", headers={
        "Content-Disposition": 'attachment; filename="starry-pages.zip"',
        "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})

@app.post("/api/pdf/rotate")
async def rotate(file: Annotated[UploadFile, File()], degrees: Annotated[int, Form()]) -> Response:
    if degrees not in (90, 180, 270):
        raise api_error(422, "旋轉角度只能是 90、180、270")
    pdf = await load_pdf(file)
    writer = PdfWriter()
    try:
        for page in pdf.pages:
            writer.add_page(page.rotate(degrees))
        return render(writer, "starry-rotated.pdf")
    finally:
        writer.close()

@app.post("/api/pdf/optimize")
async def optimize(file: Annotated[UploadFile, File()]) -> Response:
    pdf = await load_pdf(file)
    writer = PdfWriter()
    try:
        for page in pdf.pages:
            page.compress_content_streams()
            writer.add_page(page)
        return render(writer, "starry-optimized.pdf")
    except (PdfReadError, ValueError, KeyError, TypeError, OSError, IndexError) as exc:
        raise api_error(422, "無法壓縮此 PDF 內容") from exc
    finally:
        writer.close()
