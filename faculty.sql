SELECT *
FROM people_userprofile
WHERE CONCAT(first_name, ' ', last_name) IN
	(SELECT instructor_string
	FROM courses_section
	WHERE sec_term_id =
		(SELECT id
		FROM courses_term
		WHERE term_id = '2018SP')
	)
