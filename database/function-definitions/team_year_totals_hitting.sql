CREATE OR REPLACE FUNCTION team_year_totals_hitting(year integer, division integer)
RETURNS TABLE(team_id integer, ab bigint, h bigint, dbl bigint, tpl bigint, hr bigint, bb bigint, ibb bigint, hbp bigint, r bigint, rbi bigint, k bigint, sf bigint, sh bigint, dp bigint, sb bigint, cs bigint) AS $$
	BEGIN
		RETURN QUERY SELECT t.id, sum(hl.ab), sum(hl.h), sum(hl.dbl), sum(hl.tpl), sum(hl.hr), sum(hl.bb), sum(hl.ibb), sum(hl.hbp), sum(hl.r), sum(hl.rbi), sum(hl.k), sum(hl.sf), sum(hl.sh), sum(hl.dp), sum(hl.sb), sum(hl.cs)
					   FROM hitting_line as hl
					     JOIN roster AS r ON r.id = hl.roster_id
						 JOIN team AS t ON t.id = r.team_id
						 JOIN conference AS c ON c.id = t.conference_id
					   WHERE t.year = $1 AND c.division = $2
					   GROUP BY t.id;
	END;
$$ LANGUAGE plpgsql;