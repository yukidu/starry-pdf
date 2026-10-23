# 繁星 PDF v0.2 測試進度｜2026-10-23

## GitHub / 部署狀態

- 倉庫：`yukidu/starry-pdf`，**Public**（使用者已確認）。
- main：`9aafeb3c657d77e14862ff12d0d9b264c5605152`，目前只有初始 README。
- 開發 PR：[Draft #1](https://github.com/yukidu/starry-pdf/pull/1)；尚未合併 main。
- Cloudflare：**尚未部署**；沒有新建本專案 Worker / Container / D1 / R2。
- 正式網址：尚無，依使用者 C01 決議等待完整驗收與另行確認。

## 已驗證

1. GitHub `Verify (no deployment)` 基礎檢查：成功。
2. [Runtime PDF smoke 第一次實際處理測試](https://github.com/yukidu/starry-pdf/actions/runs/39923539710)：成功。
   - 真正啟動上游 Stirling PDF v3.2.1 測試容器。
   - 以無私人資料的自動生成 PDF，成功合併成 2 頁。
   - 成功拆分為 2 個單頁 PDF。
   - 成功壓縮、結果為有效的 2 頁 PDF。
   - PWA 安裝入口、manifest HTTP 檢查成功。
3. 已新增預設登入保護測試與只在 CI 隔離環境停用登入的功能測試設定；以最新 CI 結果為準。

## 授權與限制

- 上游版本：v3.2.1，commit `cb7b58a2c0c00d6350de51994e5c47317b204d85`。
- 上游是 open-core；根目錄 MIT 排除多個另行授權目錄（含 `engine/`）。
- **正式使用不能直接假設官方完整容器或受限制程式可免費改造部署；測試運行不是授權證明。**
- 這個 GitHub 倉庫目前只有 Starry PDF 的測試與評估架構，**沒有複製完整原始碼或引擎**。
- 需要設計可合法正式使用的 PDF 引擎方案，或另外取得原廠適當授權。
- PDF 的 OCR、簽名、更多轉檔、真正手機安裝、外部 HTTPS、安全登入與容量測試**均未驗收**。

## 安全規則

- 公開倉庫不放 PDF 文件、簽名、私人資料、帳密或金鑰。
- 本機 `127.0.0.1:8088` 僅允許電腦本身連線；CI 的無登入模式不對外部署。
- 禁止直接合併 PR #1 或啟動 Production；確認前不改動其他 Starry / H-Global 專案。
- 只有正式部署成功時才產生可回退代碼；目前無上線代碼。
