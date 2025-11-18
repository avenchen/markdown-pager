# GitHub Release 建立腳本
# 需要先安裝 GitHub CLI: winget install GitHub.cli

param(
    [string]$Version = "1.3.0",
    [string]$Tag = "v$Version",
    [switch]$Draft = $false
)

Write-Host "正在建立 GitHub Release..." -ForegroundColor Cyan
Write-Host ""

# 檢查執行檔是否存在
if (-not (Test-Path "dist\MarkdownPager.exe")) {
    Write-Host "錯誤：找不到 dist\MarkdownPager.exe" -ForegroundColor Red
    Write-Host "請先執行打包：.\build.bat" -ForegroundColor Yellow
    exit 1
}

# 檢查 GitHub CLI
try {
    gh --version | Out-Null
} catch {
    Write-Host "錯誤：未安裝 GitHub CLI" -ForegroundColor Red
    Write-Host "請安裝：winget install GitHub.cli" -ForegroundColor Yellow
    Write-Host "或前往：https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}

# 檢查是否已登入
try {
    gh auth status | Out-Null
} catch {
    Write-Host "錯誤：未登入 GitHub" -ForegroundColor Red
    Write-Host "請執行：gh auth login" -ForegroundColor Yellow
    exit 1
}

# 讀取版本說明
$releaseNotes = ""
if (Test-Path "version.md") {
    $versionContent = Get-Content "version.md" -Raw -Encoding UTF8
    # 提取最新版本說明
    if ($versionContent -match "(?s)## $Version.*?## \d+\.\d+\.\d+") {
        $releaseNotes = $matches[0] -replace "## $Version", "" -replace "## \d+\.\d+\.\d+.*", ""
        $releaseNotes = $releaseNotes.Trim()
    } else {
        # 如果找不到，使用第一段
        $releaseNotes = "Markdown Pager $Version`n`n詳見 version.md"
    }
} else {
    $releaseNotes = "Markdown Pager $Version"
}

Write-Host "版本：$Version" -ForegroundColor Green
Write-Host "標籤：$Tag" -ForegroundColor Green
Write-Host "執行檔：dist\MarkdownPager.exe" -ForegroundColor Green
Write-Host ""

# 確認
$confirm = Read-Host "是否繼續建立 Release？(Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "已取消" -ForegroundColor Yellow
    exit 0
}

# 建立 Release
Write-Host "正在建立 Release..." -ForegroundColor Cyan

$draftFlag = if ($Draft) { "--draft" } else { "" }

try {
    gh release create $Tag `
        --title "Markdown Pager $Version" `
        --notes $releaseNotes `
        --target main `
        $draftFlag `
        "dist\MarkdownPager.exe"
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Release 建立成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "查看 Release：" -ForegroundColor Cyan
    gh release view $Tag --web
} catch {
    Write-Host ""
    Write-Host "錯誤：建立 Release 失敗" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

