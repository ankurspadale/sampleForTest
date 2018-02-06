@ECHO OFF
SETLOCAL ENABLEDELAYEDEXPANSION
FOR /D /R %%i IN (*) DO (
    SET "n=%%~nxi"
    REN "%%i" "!n: =-!"
)