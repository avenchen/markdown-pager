@echo off
chcp 65001 >nul
echo 正在打包 Markdown Pager 為 Windows 可執行檔...
echo.

REM 檢查 PyInstaller 是否已安裝
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安裝 PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 錯誤：無法安裝 PyInstaller
        pause
        exit /b 1
    )
)

REM 清理舊的建置檔案
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo 開始打包...
echo.

REM 使用 PyInstaller 打包
python -m PyInstaller --onefile ^
    --windowed ^
    --name "MarkdownPager" ^
    --add-data "content;content" ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=json ^
    --hidden-import=pathlib ^
    --hidden-import=re ^
    --noconsole ^
    --clean ^
    always_on_top_viewer.py

if errorlevel 1 (
    echo.
    echo 打包失敗！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可執行檔位置：dist\MarkdownPager.exe
echo.
echo 請將以下檔案一起複製到目標電腦：
echo   - dist\MarkdownPager.exe
echo   - content\ 資料夾（如果需要的話）
echo.
echo 注意：可執行檔是獨立的，不需要安裝 Python
echo.

pause

