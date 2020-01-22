@choice /M "Are you sure you want to create the database?"
@if %ERRORLEVEL% == 2 GOTO END
@if %ERRORLEVEL% == 1 GOTO YES
:YES
@ECHO Creating Database...
psql -d postgres -c "CREATE DATABASE ncaa_baseball"
:END