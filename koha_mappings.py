# this translates academic_level (for students) or etype (for employees) into
# our Koha patron categories
category = {
    "Faculty": "FACULTY",
    "Graduate": "GRAD",
    "Instructors": "SPECIALFAC",
    "Staff": "STAFF",
    "Undergraduate": "UNDERGRAD",
}

# Koha faculty departments, roughly align with CCA divisions
# Values in use (as of 9/2017) are:
# 1: Architecture, 2: Design, 3: Fine Arts, 4: H&S/Critical Studies,
# 5: Visual Studies (undergrad), 6: Visual Critical Studies (grad),
# 7: Writing & Comics, 8: Wattis, 9: CAPL, 10: First Year, a: Administrative,
# b: Other/Special (interdisciplinary)
fac_depts = {
    "Academic Affairs": "a",
    "Advancement": "a",
    "All Faculty": None,
    "Animation": 3,
    "Architecture": 1,
    "Business Office": "a",
    # I think this name is defunct...
    "Center for Art and Public Life": 9,
    "Center for Impact": 9,
    "Ceramics": 3,
    "Communications": "a",
    "Community Arts": 3,
    "Creative Instructional Technologies": "a",
    # 2020 Div Studies -> CES
    "Critical Ethnic Studies": 4,
    "Critical Studies": 4,
    "Curatorial Practice": 3,
    "Design": 2,
    "Design MBA": 2,
    "Diversity Studies": 4,
    # defunct as of Fall 2021
    # "Educational Technology Services": "a",
    "Enrollment Services": "a",
    "Extension Instructor": "b",
    "Facilities": "a",
    "Fashion": 2,
    "Film": 3,
    "Financial Aid Office": "a",
    "Fine Arts": 3,
    "First Year": 10,
    "Furniture Design": 2,
    "Game Arts": 3,
    "Glass": 3,
    "Grad Comics": 7,
    "Grad Design": 2,
    "Graphic Design": 2,
    "History of Art and Visual Culture": 5,  # formerly Visual Studies
    "Humanities and Sciences": 4,
    "Human Resources": "a",
    "Illustration": 2,
    "Individualized Studies": 3,
    "Industrial Design": 2,
    "Interaction Design": 2,
    "Interdisciplinary": "b",
    "Interior Design": 2,
    "Jewelry/Metal Arts": 3,
    "Libraries": "a",
    "Masters of Architecture": 1,
    "MDes in Interaction Design": 2,
    "Office of the CIO": "a",
    "Office of the President": "a",
    "Operations": "a",
    "Painting/Drawing": 3,
    "Photography": 3,
    "PhotographyAcademic Affairs": 3,
    "Pre-College Instructor": "b",
    "Printmedia": 3,  # formerly Printmaking
    "Public Safety": "a",
    "Purchasing": "a",
    "Sculpture": 3,
    "Shipping and Receiving": "a",
    "Special Programs": "b",
    "Student Affairs": "a",
    "Student Records": "a",
    "Studio Operations": "a",  # renamed from Studio Managers, Fall 2021
    "Technology Services": "a",  # replaced ETS in Fall 2021
    "Textiles": 3,
    "Visual and Critical Studies": 6,
    "Wattis Institute": 8,
    "Writing": 7,
    "Writing & Literature": 7,
    "YASP Instructor": "b",
}

# Codes are configured in Koha's Authorized Values:
# https://library-staff.cca.edu//cgi-bin/koha/admin/authorised_values.pl
# formerly known as "PCODE3" in Millennium, "STUDENTMAJ" patron attribute in Koha
stu_major = {
    "Animation": 1,
    "Architecture": 2,
    "Ceramics": 3,
    "Community Arts": 4,
    # this one's a toss-up, putting it with MFA Design for now
    "Dual Degree: Graduate Design/Design Strategy": 24,
    # dual-degree programs for grad students
    # we arbitrarily choose to capture the non-VCS side of the degree for now
    "Dual Degree: Graduate Visual and Critical Studies/Curatorial Practice": 17,
    "Dual Degree: Graduate Visual and Critical Studies/Fine Arts": 26,
    "Dual Degree: Graduate Visual and Critical Studies/Writing": 27,
    "Fashion Design": 5,
    "Film": 6,
    "Furniture": 7,
    "Game Arts": 39,
    "Glass": 8,
    "Graduate Advanced Architectural Design": 19,
    "Graduate Architecture": 16,
    "Graduate Comics": 23,
    "Graduate Curatorial Practice": 17,
    "Graduate Design (2 year)": 24,
    "Graduate Design (3 year)": 24,
    "Graduate Design Strategy": 20,
    "Graduate Film": 25,
    "Graduate Fine Arts": 26,
    "Graduate Interaction Design": 13,
    "Graduate Visual and Critical Studies": 18,
    "Graduate Writing": 27,
    "Graphic Design": 9,
    "History of Art and Visual Culture": 34,
    "Illustration": 10,
    "Individualized Studies": 11,
    "Industrial Design": 12,
    "Interaction Design": 13,
    "Interior Design": 14,
    "Jewelry and Metal Arts": 15,
    "Painting and Drawing": 28,
    "Photography": 29,
    # Printmaking -> Printmedia 2019
    "Printmaking": 30,
    "Printmedia": 30,
    "Printmedia": 30,
    "Sculpture": 31,
    "Textiles": 32,
    "Undeclared, UG": 33,
    # defunct, VS is now "History of Art and Visual Culture" 2020-08
    "Visual Studies": 34,
    "Writing and Literature": 35,
}
