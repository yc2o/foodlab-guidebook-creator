@echo off
setlocal
set TARGET=%1
if "%TARGET%"=="" set TARGET=all

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fg.ps1" %TARGET%
endlocal
