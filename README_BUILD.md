# 打包說明

## 方法一：使用批次檔（推薦）

1. 雙擊執行 `build.bat`
2. 等待打包完成
3. 可執行檔位於 `dist\MarkdownPager.exe`

## 方法二：使用 PowerShell

1. 以系統管理員身分開啟 PowerShell
2. 執行：`.\build.ps1`
3. 等待打包完成
4. 可執行檔位於 `dist\MarkdownPager.exe`

## 方法三：手動打包

如果上述方法無法使用，可以手動執行：

```powershell
# 安裝 PyInstaller
pip install pyinstaller

# 打包
pyinstaller --onefile --windowed --name "MarkdownPager" --add-data "content;content" --clean always_on_top_viewer.py
```

## 打包後的檔案

- `dist\MarkdownPager.exe` - 單一可執行檔（包含所有依賴）

## 部署到其他電腦

1. 將 `dist\MarkdownPager.exe` 複製到目標電腦
2. 雙擊執行即可，**不需要安裝 Python**
3. （可選）如果需要預設內容，可一併複製 `content` 資料夾

## 注意事項

- 打包後的檔案較大（約 10-20 MB），因為包含了 Python 執行環境
- 首次執行可能需要幾秒鐘啟動時間
- 如果目標電腦的防毒軟體警告，這是正常現象（因為是打包的執行檔），可以加入白名單
- 設定檔 `config.json` 會在程式執行時自動建立

## 疑難排解

### 打包失敗
- 確保已安裝 Python 3.7 或更高版本
- 確保已安裝所有依賴：`pip install -r requirements.txt`（可選）

### 執行檔無法執行
- 檢查目標電腦是否為 Windows 系統
- 檢查是否有防毒軟體阻擋
- 嘗試以系統管理員身分執行

