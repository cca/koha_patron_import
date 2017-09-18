SELECT people_userprofile.username, people_userprofile.first_name, people_userprofile.last_name, people_userprofile.ccaid, people_userprofile.prodep
FROM people_userprofile
JOIN people_userprofile_groups ON (people_userprofile.id = people_userprofile_groups.userprofile_id)
JOIN auth_group ON (people_userprofile_groups.group_id = auth_group.id)
WHERE auth_group.name LIKE '%Faculty%'
ORDER BY date_joined DESC
