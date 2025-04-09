param (
    [Parameter(HelpMessage="版本信息文件路径")][string]$version_info_py_file_path = "version.py",
    [parameter(HelpMessage="项目根目录")][string]$project_dir = $PSScriptRoot
)

function Test-IsGitHubActions {
    # 检查 GITHUB_ACTIONS 环境变量是否为 "true"
    $env:GITHUB_ACTIONS -eq "true"
}

function Test-isACTIONS_STEP_DEBUG {
    # 检查 ACTIONS_STEP_DEBUG 环境变量是否为 "true"
    $env:ACTIONS_STEP_DEBUG -eq "true"
}

function Write-Debug {
    param (
        [Parameter(Mandatory=$true, Position=0, ValueFromPipeline=$true, ValueFromPipelineByPropertyName=$true)]
        [string]$Message
    )
    if (Test-IsGitHubActions)
    {
        $Line = $MyInvocation.ScriptLineNumber
        $Col = $MyInvocation.OffsetInLine
        Write-Host "::debug file=$PSCommandPath,line=$Line,col=$Col::$Message"
    }
    else
    {
        Microsoft.PowerShell.Utility\Write-Debug -Message $Message
    }
}

function Write-Warning {
    param (
        [Parameter(Mandatory=$true, Position=0, ValueFromPipeline=$true, ValueFromPipelineByPropertyName=$true)]
        [string]$Message
    )
    if (Test-IsGitHubActions)
    {
        $Line = $MyInvocation.ScriptLineNumber
        $Col = $MyInvocation.OffsetInLine
        Write-Host "::warning file=$PSCommandPath,line=$Line,col=$Col::$Message"
    }
    else
    {
        Microsoft.PowerShell.Utility\Write-Warning -Message $Message
    }
}
function Write-Error {
    param (
        [Parameter(Mandatory=$true, Position=0, ValueFromPipeline=$true, ValueFromPipelineByPropertyName=$true)]
        [string]$Message
    )
    if (Test-IsGitHubActions)
    {
        $Line = $MyInvocation.ScriptLineNumber
        $Col = $MyInvocation.OffsetInLine
        Write-Host "::error file=$PSCommandPath,line=$Line,col=$Col::$Message"
    }
    else
    {
        Microsoft.PowerShell.Utility\Write-Error -Message $Message
    }
}

if ($project_dir.Length -eq 0)
{
    Write-Warning "未指定项目根目录$project_dir, 使用当前目录${Get-Location}"
    $project_dir = Get-Location
}

# 执行前检查
if ($False -eq (Test-Path $project_dir))
{
    Write-Error "项目根目录不存在"
    exit 1
}
$is_have_git = Get-Command git -ErrorAction SilentlyContinue
if ($null -eq $is_have_git)
{
    Write-Error "未能查找到 Git 命令行工具"
    exit 1
}
$is_have_python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $is_have_python)
{
    Write-Error "未能查找到 Python"
    exit 1
}

$Location = Get-Location

Set-Location $project_dir

$is_git_repo = (git rev-parse --is-inside-work-tree 2>$null)
if ($null -eq $is_git_repo)
{
    Write-Error "工作目录${project_dir}不是 Git 仓库"
    exit 1
}

if ($env:ENABLE_SHORTHASH -eq $True){
    $git_hash = git rev-parse --short HEAD 2>$null
}
else {
    $git_hash = git rev-parse HEAD 2>$null
}

$git_tag = git rev-list --tags --max-count=1 | ForEach-Object { git describe --tags $_ --abbrev=0 } 2>$null

$git_commit_time = git log -1 --format=%cd --date=format:'%Y-%m-%d %H:%M:%S' 2>$null

$git_branch = git branch --show-current 2>$null

$build_time = Get-Date -Format "yyyy-MM-dd HH:mm:ss" 2>$null

if (Test-Path $Location)
{
    Set-Location $Location
}
else {
    Write-Warning "无法切回原始工作目录${Location}"
}

try {
    $version = $git_tag.TrimStart("v") 2>$null
}
catch {
}

$build_python_version = python --version 2>$null

$version_info_cpp = @"
git_hash = "$git_hash"
git_tag = "$git_tag"
git_commit_time = "$git_commit_time"
git_branch = "$git_branch"
build_time = "$build_time"
version = "$version"
build_python_version = "$build_python_version"
"@

Set-Content -Path $version_info_py_file_path -Value $version_info_cpp

if ($null -eq $git_hash)
{
    Write-Warning "Git hash 无法获取, 替换为'$null'"
}
if ($null -eq $git_tag)
{
    Write-Warning "Git tag 无法获取, 替换为'$null'"
}
if ($null -eq $git_commit_time)
{
    Write-Warning "Git commit time 无法获取, 替换为'$null'"
}
if ($null -eq $git_branch)
{
    Write-Warning "Git branch 无法获取, 替换为'$null'"
}
if ($null -eq $build_time)
{
    Write-Warning "Build time 无法获取, 替换为'$null'"
}
if ($null -eq $version)
{
    Write-Warning "Version 无法获取, 替换为'$null'"
}
if ($null -eq $build_python_version)
{
    Write-Warning "Python version 无法获取, 替换为'$null'"
}

if (Test-isACTIONS_STEP_DEBUG)
{
    Write-Debug "is_have_git: $is_have_git"
    Write-Debug "is_have_python: $is_have_python"
    Write-Debug "is_have_pybind11_config: $is_have_pybind11_config"
    Write-Debug "Location: $Location"
    Write-Debug "is_git_repo: $is_git_repo"
    Write-Debug "Git hash: $git_hash"
    Write-Debug "Git tag: $git_tag"
    Write-Debug "Git commit time: $git_commit_time"
    Write-Debug "Git branch: $git_branch"
    Write-Debug "Build time: $build_time"
    Write-Debug "Version: $version"
    Write-Debug "Python version: $build_python_version"
    Write-Debug "version_info_py_file_path: $version_info_py_file_path"
    Write-Debug "project_dir: $project_dir"
    Write-Debug "version_info_cpp: $version_info_cpp"
}