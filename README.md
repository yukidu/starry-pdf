# 繁星 PDF｜Starry PDF

**目前尚未部署｜GitHub 公開，正式網站尚未上線。**

繁星 PDF 是獨立的 Web First + PWA PDF 工具專案，使用者目前指定 GitHub 公開、私人使用，先建置與驗收，**完整驗收及再次確認後才准正式部署**。

## v0.2 獨立版本（開發中）
以 React + TypeScript + Vite 建立前端，以 FastAPI + [pypdf](https://github.com/py-pdf/pypdf) 建立獨立開源 PDF 處理後端，沒有複製 Stirling PDF 受限授權的引擎。首批功能：
- 合併 PDF
- 拆分 PDF
- 旋轉 PDF
- 內容壓縮（不保證檔案一定變小）

**本機測試（需 Docker Desktop）**

```sh
docker compose -f docker-compose.starry.yml up --build -d
```

同一台電腦開啟 http://127.0.0.1:8090 。
停止：`docker compose -f docker-compose.starry.yml down`。

API 不儲存個人文件，但**此本機版本沒有網際網路登入驗證，禁止將 8090 開放到公網**。正式部署前必須增加外部存取驗證、隱私防護及容量測試。詳細內容見 [STANDALONE.md](STANDALONE.md)。

## 上游 Stirling PDF 評估
原始碼來源：[Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF)；v3.2.1 不是全部 MIT，部分子目錄明確另行授權（含 engine）。舊的 `docker-compose.yml` 是**原廠容器本機評估專用**，**不能當成可自由複製的完整引擎**。詳見 `LICENSE-UPSTREAM.txt` 及 `scripts/prepare_source.py`。

## GitHub 開發與測試
- Draft PR： https://github.com/yukidu/starry-pdf/pull/1
- 分支：`feat/initial-pdf-scaffold-20261023`
- 對獨立開源版執行 12 項 PDF 核心測試、React TypeScript 建置、Docker 啟動及實際 HTTP 連線測試。
- CI 只測試，**不會執行 Cloudflare Production Deploy**。

## 仍未完成
更多 PDF 工具、OCR、簽名、轉檔、手機實機 PWA 驗收、正式登入、雲端部署與安全容量測試。公開的是程式碼，**請勿將 PDF、帳密、API 金鑰或私人資料放進 GitHub**。
