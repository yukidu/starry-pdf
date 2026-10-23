# 繁星 PDF｜Starry PDF

公開 GitHub 開發專案，預計提供 **Web First + PWA** PDF 工具，個人使用，手機與電腦共用。

**目前：尚未部署。** 本專案的 v0.1 只是本機評估、PWA 入口與授權檢查基礎；尚不是可使用的完整 PDF App。

## 架構與安全界線

- 公開的是程式碼；**個人 PDF、使用紀錄、簽章、帳密、金鑰不得上傳 GitHub**。
- 獨立 GitHub 倉庫，不修改其他 Starry / H-Global 專案。
- 先以 [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF) 官方 v3.2.1 映像進行 **本機評估**，但不表示已獲得複製其獨立授權程式的許可。
- Stirling PDF v3.2.1 的根目錄 MIT License **不包含**部分獨立授權原始碼；請見 `LICENSE-UPSTREAM.txt` 和 `scripts/prepare_source.py`。
- 此 repo **沒有完整 Stirling PDF 引擎**；取得開源快照之後仍須確認其可否單獨建置及功能完整性。

## 本機評估（不對外開放）

需安裝 Docker Desktop：

```bash
docker compose up -d
```

在同一台電腦開啟 `http://localhost:8088/install`。停止服務：`docker compose down`。

- 8088 僅綁定本機 `127.0.0.1`，不應直接開放到網際網路。
- 首次登入時應參考 Stirling PDF 官方設定，立即變更任何預設密碼。
- 官方容器的使用受到其自身授權條款限制；此階段僅供本機合法評估，不對外部署。
- 想在手機安裝／跨裝置存取，需要 HTTPS 與額外登入保護，目前**尚未完成**。

## 原始碼授權審查

```bash
python3 scripts/prepare_source.py
python3 -m unittest discover -s tests -v
```

腳本會確認官方版本 commit 和排除獨立授權目錄，授權異動時會停止。生成 `vendor/` 前必須再審查第三方依賴，請勿直接將完整原始碼當成全 MIT。

## 驗收與部署

1. 本機靜態檢查（CI）。
2. 取得並查核合法可複製的原始碼。
3. Docker 啟動與合併、拆分、壓縮、簽名、OCR、手機 PWA 功能實測。
4. 評估 Cloudflare Containers 成本及權限／文件隔離。
5. 經使用者看過預覽並另行同意後，才進行 Cloudflare 正式部署。

**狀態：正式上線尚未授權；GitHub 公開並不代表網站公開部署。**
