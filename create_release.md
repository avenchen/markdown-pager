# 建立 GitHub Release 指南

將打包好的執行檔上傳到 GitHub 作為 Release 版本。

## 方法一：使用 GitHub CLI（推薦）

### 前置需求

1. **安裝 GitHub CLI**：
   ```powershell
   winget install GitHub.cli
   ```
   或前往 https://cli.github.com/ 下載

2. **登入 GitHub**：
   ```powershell
   gh auth login
   ```
   按照提示完成登入

### 使用自動化腳本

1. **執行打包**（如果還沒打包）：
   ```powershell
   .\build.bat
   ```

2. **建立 Release**：
   ```powershell
   .\create_release.ps1
   ```

   或指定版本號：
   ```powershell
   .\create_release.ps1 -Version "1.3.0"
   ```

   建立草稿版本（先不上線）：
   ```powershell
   .\create_release.ps1 -Draft
   ```

### 手動使用 GitHub CLI

```powershell
# 建立 Release 並上傳執行檔
gh release create v1.3.0 `
    --title "Markdown Pager v1.3.0" `
    --notes "版本說明（從 version.md 複製）" `
    dist\MarkdownPager.exe
```

## 方法二：使用 GitHub 網頁介面

1. **確保執行檔已打包**：
   ```powershell
   .\build.bat
   ```

2. **前往 GitHub 儲存庫**：
   - 開啟您的 GitHub 儲存庫頁面
   - 點擊右側的 **Releases** 連結
   - 或直接前往：`https://github.com/YOUR_USERNAME/REPO_NAME/releases`

3. **建立新 Release**：
   - 點擊 **Create a new release** 或 **Draft a new release**
   - 填寫資訊：
     - **Tag version**: `v1.3.0`（建議使用語義化版本）
     - **Release title**: `Markdown Pager v1.3.0`
     - **Description**: 從 `version.md` 複製版本說明
   - 在 **Attach binaries** 區域：
     - 拖放或選擇 `dist\MarkdownPager.exe`
   - 選擇 **Publish release**（或 **Save draft** 先存為草稿）

4. **完成**：Release 建立後，使用者就可以下載執行檔了

## 版本號建議

使用[語義化版本](https://semver.org/)：
- **主版本號**（Major）：重大變更，不相容的 API 修改
- **次版本號**（Minor）：新功能，向後相容
- **修訂號**（Patch）：錯誤修正，向後相容

範例：
- `v1.0.0` - 首次正式發布
- `v1.1.0` - 新增功能
- `v1.1.1` - 錯誤修正
- `v2.0.0` - 重大更新

## 更新現有 Release

如果需要更新同一個版本的 Release：

```powershell
# 刪除舊的 Release（會同時刪除標籤）
gh release delete v1.3.0

# 重新建立
gh release create v1.3.0 --title "..." --notes "..." dist\MarkdownPager.exe
```

或直接在 GitHub 網頁上編輯 Release，重新上傳檔案。

## 自動化流程建議

可以建立一個完整的發布流程：

```powershell
# 1. 更新版本號（手動編輯 version.md）
# 2. 打包
.\build.bat

# 3. 提交變更
git add .
git commit -m "Release v1.3.0"
git push

# 4. 建立 Release
.\create_release.ps1 -Version "1.3.0"
```

## 注意事項

- 執行檔通常較大（10-20 MB），上傳可能需要一些時間
- GitHub 對單一檔案大小限制為 100 MB
- 建議在 Release 說明中包含：
  - 版本號
  - 主要變更
  - 系統需求
  - 使用說明連結

## 疑難排解

### GitHub CLI 未安裝
```powershell
winget install GitHub.cli
```

### 未登入 GitHub
```powershell
gh auth login
```

### 找不到遠端儲存庫
```powershell
# 檢查遠端設定
git remote -v

# 如果沒有，添加遠端
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

