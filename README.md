# Markdown Pager

一個現代化的 always-on-top Markdown 檢視器，支援章節導航、快捷鍵操作與自訂設定。

## 功能特色

- 🎨 **現代化深色 UI**：統一的配色方案與扁平化設計
- 📄 **章節導航**：自動解析 Markdown 檔案中的 `# ` 標題，支援章節切換
- ⌨️ **快捷鍵支援**：
  - 方向鍵：上一頁（↑）、下一頁（↓）、首頁（←）、最後（→）
  - Ctrl + 字母：可在設定中自訂（預設 H/P/N/L）
  - Ctrl +/−：調整字級大小
- ⚙️ **豐富設定**：
  - 視窗透明度調整（0.3-1.0）
  - 視窗大小自訂
  - 顯示區字級調整（8-24px）
  - 快捷鍵自訂
- 💾 **設定保存**：自動保存視窗位置、大小、透明度等設定
- 🔄 **Always on Top**：視窗始終保持在最上層

## 系統需求

- Windows 10/11
- Python 3.7+（開發環境，執行檔不需要）

## 安裝與使用

### 方式一：使用執行檔（推薦）

1. 下載 `MarkdownPager.exe`
2. 雙擊執行即可，無需安裝 Python

### 方式二：從原始碼執行

1. 安裝依賴（可選，用於更好的 Markdown 渲染）：
   ```powershell
   pip install -r requirements.txt
   ```

2. 執行程式：
   ```powershell
   python always_on_top_viewer.py
   ```

## 打包

如需自行打包為執行檔：

```powershell
# 使用批次檔
.\build.bat

# 或使用 PowerShell
.\build.ps1
```

詳細說明請參考 [README_BUILD.md](README_BUILD.md)

## 使用說明

1. **選擇檔案**：點擊「設定」→「選擇 Markdown 檔」載入檔案
2. **章節導航**：
   - 使用工具列按鈕：首頁、上一頁、下一頁、最後
   - 使用方向鍵：←、↑、↓、→
   - 使用快捷鍵：Ctrl + 自訂字母
3. **調整設定**：點擊「設定」按鈕開啟設定視窗
4. **拖動視窗**：點擊視窗任意位置（非按鈕區域）可拖動

## 專案結構

```
demo-ppt/
├── always_on_top_viewer.py  # 主程式
├── build.bat                 # 打包腳本（批次檔）
├── build.ps1                 # 打包腳本（PowerShell）
├── requirements.txt          # Python 依賴（可選）
├── README.md                 # 本文件
├── README_BUILD.md           # 打包說明
├── spec.md                   # 功能規格
├── version.md                # 版本紀錄
├── task.md                   # 任務清單
├── content/                  # 範例內容
│   └── pages/
│       ├── home.md
│       ├── guide.md
│       └── all.md
└── logs/                     # 執行紀錄
    └── 2025-11-17.md
```

## 開發

### 技術棧

- Python 3.7+
- tkinter（GUI）
- json（設定保存）
- PyInstaller（打包）

### 可選依賴

- `markdown`：更好的 Markdown 渲染（HTML 模式）
- `tkhtmlview`：HTML 顯示支援

## 授權

本專案為個人專案，可自由使用與修改。

## 版本歷史

詳見 [version.md](version.md)

## 問題回報

如有問題或建議，請在 GitHub Issues 中提出。

