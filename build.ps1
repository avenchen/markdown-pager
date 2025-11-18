# PowerShell 打包腳本
Write-Host "正在打包 Markdown Pager 為 Windows 可執行檔..." -ForegroundColor Cyan
Write-Host ""

# 檢查 PyInstaller 是否已安裝
try {
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "正在安裝 PyInstaller..." -ForegroundColor Yellow
        pip install pyinstaller
        if ($LASTEXITCODE -ne 0) {
            Write-Host "錯誤：無法安裝 PyInstaller" -ForegroundColor Red
            Read-Host "按 Enter 鍵退出"
            exit 1
        }
    }
} catch {
    Write-Host "正在安裝 PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# 清理舊的建置檔案
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
Get-ChildItem -Filter "*.spec" | Remove-Item -Force

Write-Host "開始打包..." -ForegroundColor Green
Write-Host ""

# 使用 PyInstaller 打包
$pyinstallerArgs = @(
    "--onefile",
    "--windowed",
    "--name", "MarkdownPager",
    "--add-data", "content;content",
    "--hidden-import=tkinter",
    "--hidden-import=tkinter.filedialog",
    "--hidden-import=tkinter.messagebox",
    "--hidden-import=json",
    "--hidden-import=pathlib",
    "--hidden-import=re",
    "--noconsole",
    "--clean",
    "always_on_top_viewer.py"
)

python -m PyInstaller @pyinstallerArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "打包失敗！" -ForegroundColor Red
    Read-Host "按 Enter 鍵退出"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "打包完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "可執行檔位置：dist\MarkdownPager.exe" -ForegroundColor Yellow
Write-Host ""
Write-Host "請將以下檔案一起複製到目標電腦：" -ForegroundColor Cyan
Write-Host "  - dist\MarkdownPager.exe"
Write-Host "  - content\ 資料夾（如果需要的話）"
Write-Host ""
Write-Host "注意：可執行檔是獨立的，不需要安裝 Python" -ForegroundColor Green
Write-Host ""

Read-Host "按 Enter 鍵退出"

