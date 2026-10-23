# 繁星 PDF｜2026-10-23 最新開發 checkpoint（v0.2）

## 真實 GitHub / Cloudflare 狀態

- GitHub Repo: https://github.com/yukidu/starry-pdf ，**Public**（使用者最新決定）。
- GitHub `main`: `9aafeb3c657d77e14862ff12d0d9b264c5605152`（仍為初始 README）。
- 開發分支：`feat/initial-pdf-scaffold-20261023`。
- 開發版 commit：`486628aa0d32a9cee0f2576d07290985ba7e1a4a`。
- PR: https://github.com/yukidu/starry-pdf/pull/1 （Draft、未合併）。
- Cloudflare Production: **尚未部署**，沒有本專案正式網址；不修改其他 Starry App。
- 以上查核日期：2026-10-23，接手後仍以 GitHub `main` 最新即時狀態為準。

## 已完成且有實測證據

**第一階段：官方 Stirling PDF 本機評估（不是自由複製授權）**
- [Stirling PDF 影音及 PDF 處理容器 smoke](https://github.com/yukidu/starry-pdf/actions/runs/39923539710)：PDF 合併、拆分、壓縮及 PWA 入口檢查成功。
- [登入安全驗證](https://github.com/yukidu/starry-pdf/actions/runs/39923987011)：未登入的 PDF 操作回應 HTTP 401。

**第二階段：真正獨立的 Starry PDF 程式碼**
- 前端：React + TypeScript + Vite，手機與桌面自適應；PWA manifest、Service Worker 不快取 PDF。
- 後端：FastAPI + BSD-3-Clause 授權 `pypdf`，完全不依賴 Stirling PDF 另行授權的 `engine/`。
- 首批 4 功能：合併（2–6 檔）、拆分（指定頁碼輸出 ZIP）、旋轉（90/180/270 度）、內容壓縮（不保證縮小）。
- 文件僅於請求期間處理，不設文件資料庫或永久儲存。
- 檔案大小、份數與頁數有限制；超限／假 PDF／加密 PDF 有錯誤處理。
- 新的本機 Docker 配置 `docker-compose.starry.yml` 限制綁定 `127.0.0.1:8090`，使用低權限網頁伺服器與只讀執行環境。

**真正端到端驗收證明**
- [GitHub Actions run #39927798961](https://github.com/yukidu/starry-pdf/actions/runs/39927798961)：**Success**。
- 12 項 Python PDF 核心及驗證測試通過（另有 1 項非阻斷 warning）。
- React TypeScript 正式編譯成功。
- Docker 雙服務實際啟動；首頁、後端健康檢查、合併、拆分、旋轉、內容壓縮、PWA manifest 都通過 HTTP 實測。
- 這些是**暫時測試環境**結果，測完已清除，不代表正式網站上線或手機實機驗收。

## 仍未完成／不可宣稱

- Stirling PDF 原版全部功能的合法完整重建；現階段只做首批四項功能。
- OCR、電子簽名、影像及 Office 轉檔、加密、工具批次作業。
- PWA 手機／桌面真機安裝驗證、跨裝置 HTTPS。
- 正式網站登入授權（建議 Cloudflare Access）、檔案防毒、安全稽核、流量／用量限制與針對 2000 人以上使用的效能測試。
- Cloudflare Container 成本核算、Cloudflare Preview、Production、正式網址與 Production 還原代碼。
- 不應在正式公開入口上直接部署目前沒有登入保護的本機 Web API。

## 法律 / 安全 / 開發 SOP

- 上游 Stirling PDF v3.2.1 根目錄 MIT 並不涵蓋所有程式；`engine/` 等目錄採不同授權；原官方容器僅用於授權允許的本機評估。
- 可合法整合的 `pypdf` 參考授權：https://github.com/py-pdf/pypdf/blob/main/LICENSE 。
- 公開 GitHub 程式碼中不能出現個人 PDF、金鑰、Token、會員或使用者資料。
- 新開發皆安全分支 → 測試 → Draft PR → 使用者檢查 → 後續正式部署另行確認。
- **PR #1 不合併，禁止 Production 部署**，因使用者指定 C01。
- 目前開發 checkpoint: `486628aa0d32a9cee0f2576d07290985ba7e1a4a`（**非** Production rollback code）。
