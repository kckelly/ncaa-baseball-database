CREATE OR REPLACE FUNCTION team_year_totals_pitching(year integer, division integer)
RETURNS TABLE(team_id integer, app bigint, gs bigint, ord bigint, w bigint, l bigint, sv bigint, ip float, p bigint, bf bigint, h bigint, dbl bigint, tpl bigint, hr bigint, bb bigint, ibb bigint, hbp bigint, r bigint, er bigint, ir bigint, irs bigint, fo bigint, go bigint, k bigint, kl bigint, sf bigint, sh bigint, bk bigint, wp bigint, cg bigint, sho bigint) AS $$
	BEGIN
		RETURN QUERY SELECT t.id, sum(pl.app), sum(pl.gs), sum(pl.ord), sum(pl.w), sum(pl.l), sum(pl.sv), sum(pl.ip), sum(pl.p), sum(pl.bf), sum(pl.h), sum(pl.dbl), sum(pl.tpl), sum(pl.hr), sum(pl.bb), sum(pl.ibb), sum(pl.hbp), sum(pl.r), sum(pl.er), sum(pl.ir), sum(pl.irs), sum(pl.fo), sum(pl.go), sum(pl.k), sum(pl.kl), sum(pl.sf), sum(pl.sh), sum(pl.bk), sum(pl.wp), sum(pl.cg), sum(pl.sho)
					   FROM pitching_line as pl
					   	 JOIN roster AS r ON r.id = pl.roster_id
						 JOIN team AS t ON t.id = r.team_id
						 JOIN conference AS c ON c.id = t.conference_id
					   WHERE t.year = $1 AND c.division = $2
					   GROUP BY t.id;
	END;
$$ LANGUAGE plpgsql;