@choice /M "Are you sure you want to delete the database?"
@if %ERRORLEVEL% == 2 GOTO END
@if %ERRORLEVEL% == 1 GOTO YES
:YES
@ECHO Deleting Database...
psql -d postgres -c "DROP DATABASE IF EXISTS ncaa_baseball"
:END
pause