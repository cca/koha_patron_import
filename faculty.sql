SELECT username, first_name, last_name, ccaid, prodep
FROM people_userprofile
-- this is an imprecise measure...staff with the same name
-- will also be pulled but that doesn't cause problems
WHERE CONCAT(first_name, ' ', last_name) IN
	(SELECT instructor_string
	FROM courses_section
	WHERE sec_term_id =
		(SELECT id
		FROM courses_term
		WHERE term_id = '2018FA')
	)
