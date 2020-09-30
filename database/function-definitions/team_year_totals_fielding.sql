CREATE OR REPLACE FUNCTION team_year_totals_fielding(year integer, division integer)
RETURNS TABLE(team_id integer, po bigint, a bigint, e bigint, pb bigint, ci bigint, sb bigint, cs bigint, dp bigint, tp bigint) AS $$
	BEGIN
		RETURN QUERY SELECT t.id, sum(fl.po), sum(fl.a), sum(fl.e), sum(fl.pb), sum(fl.ci), sum(fl.sb), sum(fl.cs), sum(fl.dp), sum(fl.tp)
					   FROM fielding_line as fl
					     JOIN roster AS r ON r.id = fl.roster_id
						 JOIN team AS t ON t.id = r.team_id
						 JOIN conference AS c ON c.id = t.conference_id
					   WHERE t.year = $1 AND c.division = $2
					   GROUP BY t.id;
	END;
$$ LANGUAGE plpgsql;