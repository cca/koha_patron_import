# Koha patron categories, see the codes listed on
# /cgi-bin/koha/admin/categorie.pl
category = {
    'UG': 'UNDERGRAD',
    'GR': 'GRAD'
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
