# GitHub 儲存庫設定指南

## 步驟 1：在 GitHub 建立新儲存庫

1. 登入 [GitHub](https://github.com)
2. 點擊右上角的 **+** → **New repository**
3. 填寫儲存庫資訊：
   - **Repository name**: `markdown-pager`（或您喜歡的名稱）
   - **Description**: `Always-on-top Markdown viewer with section navigation`
   - **Visibility**: 選擇 Public 或 Private
   - **不要**勾選 "Initialize this repository with a README"（因為我們已經有本地檔案）
4. 點擊 **Create repository**

## 步驟 2：連接本地儲存庫到 GitHub

GitHub 會顯示設定指引，執行以下命令：

```powershell
# 添加遠端儲存庫（將 YOUR_USERNAME 和 REPO_NAME 替換為您的資訊）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 將分支重新命名為 main（如果 GitHub 使用 main 而非 master）
git branch -M main

# 推送所有檔案到 GitHub
git push -u origin main
```

## 步驟 3：驗證

1. 重新整理 GitHub 頁面，應該可以看到所有檔案
2. README.md 會自動顯示在儲存庫首頁

## 後續更新

之後要更新 GitHub 上的程式碼：

```powershell
# 添加變更
git add .

# 提交變更
git commit -m "描述您的變更"

# 推送到 GitHub
git push
```

## 注意事項

- `config.json` 已在 `.gitignore` 中，不會被上傳（包含個人設定）
- `build/` 和 `dist/` 目錄也不會上傳（建置產物）
- 如果需要分享範例設定，可以手動上傳 `config.json.example`

## 可選：建立 Release

1. 在 GitHub 儲存庫頁面，點擊 **Releases** → **Create a new release**
2. 填寫版本資訊：
   - **Tag version**: `v1.2.0`
   - **Release title**: `Markdown Pager v1.2`
   - **Description**: 從 `version.md` 複製版本說明
3. 上傳 `dist/MarkdownPager.exe` 作為附件
4. 點擊 **Publish release**

這樣使用者就可以直接下載執行檔了！

