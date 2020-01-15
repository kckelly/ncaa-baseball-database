@ECHO off
choice /M "Are you sure you want to delete database?"
if %ERRORLEVEL% == 2 GOTO END
if %ERRORLEVEL% == 1 GOTO YES
:YES
ECHO Deleting Database...
psql -f delete.sql ncaabaseball
pause
:END