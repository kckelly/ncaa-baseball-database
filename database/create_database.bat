@choice /M "Are you sure you want to create database?"
@if %ERRORLEVEL% == 2 GOTO END
@if %ERRORLEVEL% == 1 GOTO YES
:YES
@ECHO Creating Database...
copy /b /y table-definitions\year_info.sql + ^
table-definitions\conference.sql + ^
table-definitions\school.sql + ^
table-definitions\coach.sql + ^
table-definitions\stadium.sql + ^
table-definitions\team.sql + ^
table-definitions\player.sql + ^
table-definitions\roster.sql + ^
table-definitions\game.sql + ^
table-definitions\inning.sql + ^
table-definitions\play_by_play.sql + ^
table-definitions\game_position.sql + ^
table-definitions\hitting_line.sql + ^
table-definitions\pitching_line.sql + ^
table-definitions\fielding_line.sql + ^
table-definitions\umpire.sql + ^
table-definitions\game_umpire.sql + ^
csv-data\copy.sql ^
create.sql
psql -f create.sql ncaabaseball
pause
:END