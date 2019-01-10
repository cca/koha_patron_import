# Koha patron categories, see the codes listed on
# /cgi-bin/koha/admin/categorie.pl
category = {
    'UG': 'UNDERGRAD',
    'GR': 'GRAD'
}

# Koha faculty departments, roughly align with CCA divisions
# set to "None" to leave FACDEPT undefined for a value
# Values in use (as of 9/2017) are:
# 1: Architecture, 2: Design, 3: Fine Arts, 4: H&S/Critical Studies,
# 5: Visual Studies (undergrad), 6: Visual Critical Studies (grad),
# 7: Writing & Comics, 8: Wattis, 9: CAPL, 10: First Year, a: Administrative,
# b: Other/Special
fac_depts = {
    "": None,
    "Academic Affairs": 'a',
    "All Faculty": None,
    "Animation": 3,
    "Architecture": 1,
    "Center for Art and Public Life": 9,
    "Ceramics": 3,
    "Community Arts": 3,
    "Critical Studies": 4,
    "Curatorial Practice": 3,
    "Design MBA": 2,
    "Diversity Studies": 4,
    "Fashion": 2,
    "Film": 3,
    "Fine Arts": 3,
    "First Year": 10,
    "Furniture Design": 2,
    "Glass": 3,
    "Grad Comics": 7,
    "Grad Design": 2,
    "Graphic Design": 2,
    "Human Resources": 'a',
    "Illustration": 2,
    "Individualized Studies": 3,
    "Industrial Design": 2,
    "Interaction Design": 2,
    "Interdisciplinary": 'b',
    "Interior Design": 2,
    "Jewelry/Metal Arts": 3,
    "Masters of Architecture": 1,
    "MDes in Interaction Design": 2,
    "Painting/Drawing": 3,
    "Photography": 3,
    "PhotographyAcademic Affairs": 3,
    "Printmaking":3 ,
    "Sculpture": 3,
    "Special Programs": 'b',
    "Textiles": 3,
    "Visual Studies": 5,
    "Visual and Critical Studies": 6,
    "Writing & Literature": 7,
    "Writing": 7,
}

# Codes are configured in Koha's Authorized Values:
# /cgi-bin/koha/admin/authorised_values.pl
# formerly known as "PCODE3" in Millennium, "STUDENTMAJ" patron attribute in Koha
major = {
    'ANIMA.BFA': 1,
    'ARCHT.BARC': 2,
    # Civic Innovation MBA, introduced Fall 2015
    # combine with Design MBA which iniated the program
    'CIMBA.MBA': 20,
    'CERAM.BFA': 3,
    'COMIC.MFA': 23,
    'COMAR.BFA': 4,
    'CURPR.MA': 17,
    # combo Design MFA + Design Strategy MBA dual degree, we put with Design
    'DD2ST': 24,
    'DESGN.MFA': 24,
    'DESST.MBA': 20,
    # these DVC** "programs" are for dual-degree grad students
    # we arbitrarily choose to capture the non-VCS side of the degree for now
    'DVCCP': 17,  # Dual Degree Vis. Crit/Curatorial Practice
    'DVCFA': 26,  # Dual Degree Vis. Crit/Fine Arts
    'DVCWR': 27,  # Dual Degree Vis. Crit/Writing
    #'EXTED': '   ',  # extended, leave null
    'FASHN.BFA': 5,
    'FCERM.MFA': 26,  # a few Fine Art MFAs share codes with their BFAs
    'FDRPT.MFA': 26,  # Drawing / Painting
    'FGLAS.MFA': 26,
    'FILMG.MFA': 25,
    'FILMS.BFA': 6,
    'FINAR.MFA': 26,
    'FLVID.BFA': 6,  # Film/Video BFA, classify with Film BFA, why does this exist?
    'FMEDA.MFA': 26,
    'FPHOT.MFA': 26,
    'FPRNT.MFA': 26,
    'FRNTR.BFA': 7,
    'FSCUL.MFA': 26,
    'FSOCP.MFA': 26,  # social practice, lump into MFA Fine Arts
    'FTEXT.MFA': 26,
    'GLASS.BFA': 8,
    'GRAPH.BFA': 9,  # if a few places we have BFA & MFA programs
    'GRAPH.MFA': 9,  # under the same PCODE number
    'ILLUS.BFA': 10,
    'INACT.MFA': 24,  # plain ol' Design MFA, not Interaction Design
    'INDIV.BFA': 11,
    'INDUS.BFA': 12,
    'INDUS.MFA': 12,
    'INTER.BFA': 14,
    # Master's of Design in Interaction Design, new 2015
    # classify with Interaction Design BFA
    'IXDGR.MDES': 13,
    'IXDSN.BFA': 13,
    'MAAD1.MAAD': 19,
    'MAAD2.MAAD': 19,
    'MAAD3.MAAD': 19,
    'MARCH.MARC': 16,
    'MARC2.MARC': 16,
    'MARC3.MARC': 16,
    'METAL.BFA': 15,
    'NODEG.UG': 37,  # "Undergraduate Non-Degree Program"
    'PHOTO.BFA': 29,
    'PNTDR.BFA': 28,
    'PPMBA.MBA': 21,  # Public Policy MBA
    #'PRECO': '   ',  # leave null, pre-college
    'PRINT.BFA': 30,
    'SCULP.BFA': 31,
    'SFMBA.MBA': 22,  # Strategic Foresight MBA
    'SOCPR.MA': 36,  # Social Practice MA, new Fall 2016
    'TEXTL.BFA': 32,
    'UNDEC.BFA': 33,
    'VISCR.MA': 18,
    'VISST.BA': 34,
    'WRITE.MFA': 27,
    'WRLIT.BA': 35
}
