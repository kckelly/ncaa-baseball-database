@choice /M "Are you sure you want to add all tables?"
@if %ERRORLEVEL% == 2 GOTO END
@if %ERRORLEVEL% == 1 GOTO YES
:YES
@ECHO Adding all Tables to Database...
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
function-definitions\player_year_totals_fielding.sql + ^
function-definitions\player_year_totals_hitting.sql + ^
function-definitions\player_year_totals_pitching.sql + ^
function-definitions\team_year_totals_fielding.sql + ^
function-definitions\team_year_totals_hitting.sql + ^
function-definitions\team_year_totals_pitching.sql + ^
copy.sql ^
add_tables.sql
psql -f add_tables.sql ncaa_baseball
pause
:END