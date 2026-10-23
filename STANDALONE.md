# 繁星 PDF v0.2｜獨立開源核心（開發預覽）

## 目前提供的功能
- PDF 合併：一次 2～6 個 PDF
- PDF 拆分：指定頁碼為多個單頁 PDF，結果下載為 ZIP
- PDF 旋轉：90 / 180 / 270 度
- PDF 內容壓縮：僅重新壓縮內容串流；**不保證檔案縮小**，尚未提供圖片重採樣。
- 手機／桌面響應式 React UI + PWA manifest；尚未完成手機真機安裝驗收。

## 重大授權決策
核心用 [pypdf](https://github.com/py-pdf/pypdf)，BSD 3-Clause 授權（可合法整合、修改與營利，但須遵守授權條件）。此 repo 只列出依賴，不把 pypdf 或受 Stirling PDF 獨立授權限制的程式碼複製進來。pypdf 原始授權：https://github.com/py-pdf/pypdf/blob/main/LICENSE

Stirling PDF 的官方完整 Docker 映像仍只留作**本機評估測試**，無法以 MIT 根授權推論可自行複製其 `engine/` 等部分。獨立 app 的 `api/` 與 `app-web/` 不依賴該映像。

## 本機啟動（**不得直接公開到網際網路**）
需 Docker Desktop，在本 repo 根目錄：

```sh
docker compose -f docker-compose.starry.yml up --build -d
```
瀏覽器開啟 `http://127.0.0.1:8090`。

停止並移除：
```sh
docker compose -f docker-compose.starry.yml down
```

**強制僅綁定 127.0.0.1**。此版本還沒有網際網路使用者登入驗證，不可直接接 Cloudflare 公開路由。

## 安全與限制
- 不設文件資料庫、不持久化儲存 PDF；API 使用記憶體處理文件，回應禁止快取，PWA Service Worker 也不快取文件。
- 單檔上限 12 MB、最多 6 檔、每次合計最多 400 頁；這不是 2000 人的正式服務容量承諾。
- 文件可能包含不安全內容；正式對外公開前仍需文件掃毒、安全隔離、身分驗證、流量限制、容量測試、依賴更新與弱點掃描。
- 本機 HTTP 可測試功能但不是可跨裝置安裝 PWA 的 HTTPS 正式網站。

## 開發與測試
後端：`api/main.py`（FastAPI + pypdf）；前端：`app-web/src/App.tsx`（React/TypeScript/Vite）。

```sh
python -m pip install -r api/requirements-dev.txt
python -m pytest -q tests/test_engine.py
cd app-web && npm install && npm run build
```

GitHub Actions `standalone.yml` 會執行單元測試、前端建置、Docker 起動、實際 PDF HTTP API 與 PWA manifest 測試；**不含部署步驟**。

## 尚未完成
OCR、簽名、文件加密、圖片／Office 轉檔、實機 PWA、正式登入閘門和 Cloudflare Production 都未完成，PR #1 保持 Draft，不合併 main。
