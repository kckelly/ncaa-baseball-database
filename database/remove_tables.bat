@ECHO off
choice /M "Are you sure you want to remove all tables from the database?"
if %ERRORLEVEL% == 2 GOTO END
if %ERRORLEVEL% == 1 GOTO YES
:YES
ECHO Dropping all Tables from Database...
psql -f remove_tables.sql ncaa_baseball
pause
:END