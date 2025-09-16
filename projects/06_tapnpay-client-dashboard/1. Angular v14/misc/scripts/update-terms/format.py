import os, re

LIST_ITEM_HEADER_REPLS = (
    (r'^\d*\.[\.\d]*\s+', r''),
    (r'^([^\.]+\.?)', r'<strong>\1</strong>'),
)

data = [ 'en', 'es' ]

for i, lang in enumerate(data):
    filePath = './tnc_{}.html'.format(lang)

    with open(filePath, 'r', encoding='utf-8') as f:
        destFilePath = '{}.terms.html'.format(lang)
        data[i] = (lang, destFilePath, [ line.strip() for line in f.readlines() ])

commands = (
    (1, '<h2>', '</h2>', {}),
    (3, '<p>', '</p>', {
        'en': (
            (r'^(Last Updated:)', r'<strong>\1</strong>'),
        ),  
        'es': (
            (r'^(Última Actualización:)', r'<strong>\1</strong>'),
        ),  
    }),
    (5, '<p>', '</p>', {
        'en': (
            (r'"(SERVICE|AET)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            (r'"(SERVICIO|AET)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (6, '<p>', '</p>', {
        'en': (
            (r'"(AGREEMENT)"', r'"<strong>\1</strong>"'),
            (r'^(BY CLICKING "I ACCEPT," OR OTHERWISE ACCESSING OR USING THE SERVICE,)', r'<strong>\1</strong>'),
        ),
        'es': (
            (r'"(ACUERDO)"', r'"<strong>\1</strong>"'),
            (r'^(AL HACER CLIC EN "ACEPTO" O DE OTRA MANERA AL ACCEDER O UTILIZAR EL SERVICIO,)', r'<strong>\1</strong>'),
        )   
    }),
    (7, '<p>', '</p>', {
        'en': (
            (r'^(ARBITRATION NOTICE\.)', r'<strong>\1</strong>'),
        ),
        'es': (
            (r'^(AVISO DE ARBITRAJE\.)', r'<strong>\1</strong>'),
        )   
    }),
    (9, '<ol class="list list_section"><li>', '', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )
    }),
    (10, '<ol class="list list_section"><li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Tolls|Toll|ATFOs|ATFO|Carrier)"', r'"<strong>\1</strong>"'),
        ),   
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Peajes|Peaje|ATFOs|ATFO|Operador)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (11, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(LPN|Mobile Phone Number|Account)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(LPN|Número de Teléfono Móvil|Cuenta)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (12, '<li>', '<br>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )   
    }),
    (13, '', '<br><br>', {
        'en': (
            (r'"(SMS)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            (r'"(SMS)"', r'"<strong>\1</strong>"'),
        )  
    }),
    (14, '', '<br><br>', {}),
    (15, '', '<br><br>', {}),
    (16, '', '<br><br>', {
        'en': (
            (r'"STOP" to', r'"<strong>STOP</strong>" to'),
            (r'(Note that if you choose to opt out of all SMS messages and sent a "STOP" message, you will no longer be able to use the Service\.)', r'<strong>\1</strong>'),
        ),
        'es': (
            (r'"STOP" al', r'"<strong>STOP</strong>" al'),
            (r'(Tenga en cuenta que al escoger darse de baja de todos los SMS y enviar el mensaje de "STOP", no podrá seguir utilizando del Servicio\.)', r'<strong>\1</strong>'),
        )  
    }),
    (17, '', '</li></ol></li>', {
        'en': (
            (r'"(HELP)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            (r'"(HELP)"', r'"<strong>\1</strong>"'),
        )  
    }),
    (18, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )   
    }),
    (19, '<li>', '', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Beta Service|Beta Terms)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Servicio Beta|Términos Beta)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (20, '<ol class="list list_section"><li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )
    }),
    (21, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )
    }),
    (22, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )
    }),
    (23, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Feedback)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Retroalimentación)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (24, '<li>', '</li></ol></li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Confidential Information)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Información Confidencial)"', r'"<strong>\1</strong>"'),
        )   
    }),

    # START: sublist
    # 4.
    (25, '<li>', '', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )   
    }),
    # 4.1
    (26, '<ol class="list list_section"><li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        ) 
    }),
    # 4.2
    (27, '<li>', '</li></ol></li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        ) 
    }),
    # END: sublist

    # START: sublist
    (28, '<li>', '', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        ) 
    }),
    (29, '<ol class="list list_section"><li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        ) 
    }),
    (30, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        ) 
    }),
    (31, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        ) 
    }),
    (32, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(tapNpay Site)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Sitio)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (33, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        ) 
    }),
    (34, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(HELP)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(HELP)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (35, '<li>', '</li></ol></li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(HELP)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(HELP)"', r'"<strong>\1</strong>"'),
        ) 
    }),
    # END: sublist

    (36, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )   
    }),

    # START: sublist
    (37, '<li>', '', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )   
    }),
    (38, '<ol class="list list_section"><li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )   
    }),
    (39, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'have 23 hours', r'have <strong>23 hours</strong>'),
            (r'(All payments are final and non-refundable\.)', r'<strong>\1</strong>'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'tendrá 23 horas para', r'tendrá <strong>23 horas</strong> para'),
            (r'(Todos los pagos son definitivos y no reembolsables\.)', r'<strong>\1</strong>'),
        )   
    }),
    (40, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (41, '<li>', '</li></ol></li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    # END: sublist

    # START: sublist
    (42, '<li>', '', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (43, '<ol class="list list_section"><li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (44, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (45, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (46, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (47, '<li>', '</li></ol></li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    # END: sublist

    (48, '<li>', '<br><br>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (49, '', '<br><br>', {}),
    (50, '', '</li>', {}),

    (51, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(AET Entities)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Entidades de AET)"', r'"<strong>\1</strong>"'),
        )   
    }),

    # START: sublist
    (52, '<li>', '', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )   
    }),
    (53, '<ol class="list list_section"><li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[0],
        ),
        'es': (
            LIST_ITEM_HEADER_REPLS[0],
        )   
    }),
    (54, '<li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[0],
        ),
        'es': (
            LIST_ITEM_HEADER_REPLS[0],
        )   
    }),
    (55, '<li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[0],
        ),
        'es': (
            LIST_ITEM_HEADER_REPLS[0],
        )  
    }),
    (56, '<li>', '</li></ol></li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[0],
        ),
        'es': (
            LIST_ITEM_HEADER_REPLS[0],
        )  
    }),
    # END: sublist

    # START: sublist
    (57, '<li>', '', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )   
    }),
    (58, '<ol class="list list_section"><li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )   
    }),
    (59, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )   
    }),
    (60, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(AAA Rules|AAA)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Reglas de la AAA|AAA)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (61, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Notice of Arbitration|Demand)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Aviso de Arbitraje|Demanda)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (62, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (63, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (64, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (65, '<li>', '</li></ol></li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    # END: sublist

    (66, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),

    # START: sublist
    (67, '<li>', '', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (68, '<ol class="list list_section"><li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (69, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    (70, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Materials)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Materiales)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (71, '<li>', '</li>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Additional Terms)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
            (r'"(Términos Adicionales)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (72, '<li>', '</li></ol></li></ol>', {
        'en': (
            *LIST_ITEM_HEADER_REPLS,
        ),
        'es': (
            *LIST_ITEM_HEADER_REPLS,
        )    
    }),
    # END: sublist

    (74, '<h2>', '</h2>', {}),
    (76, '<p>', '</p>', {
        'en': (
            (r'"(AETolls,|we,|our,|us|Services|Privacy Policy|Users,|your|you)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            (r'"(AETolls|nosotros|nuestro|Servicios|Usuarios|su)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (78, '<h3>', '</h3>', {}),
    (80, '<p>', '</p>', {}),
    (81, '<p>', '</p>', {}),
    (82, '<ol class="list list_letter"><li><strong>', '</strong>', {
        'en': (
            (r'^[A-Z]\.\s*', r''),
        ),
        'es': (
            (r'^[A-Z]\.\s*', r''),
        )   
    }),
    (83, '<ul class="list list_dot"><li>', '</br></br>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
            (r'"(ATFOs|Carrier|LPNs)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
            (r'"(ATFOs|Operador|LPNs)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (84, '', '</li>', {}),
    (85, '<li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),
    (86, '<li>', '</li></ul></li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),

    (87, '<li><strong>', '</strong>', {
        'en': (
            (r'^[A-Z]\.\s*', r''),
        ),
        'es': (
            (r'^[A-Z]\.\s*', r''),
        )   
    }),
    (88, '<ul class="list list_dot"><li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
            (r'"(IP)"', r'"<strong>\1</strong>"'),
        ),
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
            (r'"(IP)"', r'"<strong>\1</strong>"'),
        )   
    }),
    (89, '<li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ), 
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        ), 
    }),
    (90, '<li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),  
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),
    (91, '<li>', '</br></br>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),  
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),
    (92, '', '</li></ul></li>', {}),


    (93, '<li><strong>', '</strong>', {
        'en': (
            (r'^[A-Z]\.\s*', r''),
        ), 
        'es': (
            (r'^[A-Z]\.\s*', r''),
        )   
    }),
    (94, '<ul class="list list_dot"><li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),  
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),
    (95, '<li>', '</li></ul></li></ol>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),  
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),

    (97, '<h3>', '</h3>', {}),
    (99, '<p>', '</p>', {}),

    (100, '<ul class="list list_dot"><li>', '</li>', {}),
    (101, '<li>', '</li>', {}),
    (102, '<li>', '</li>', {}),
    (103, '<li>', '</li>', {}),
    (104, '<li>', '</li>', {}),
    (105, '<li>', '</li>', {}),
    (106, '<li>', '</li>', {}),
    (107, '<li>', '</li>', {}),
    (108, '<li>', '</li>', {}),
    (109, '<li>', '</li></ul>', {}),

    (111, '<h3>', '</h3>', {}),
    (113, '<p>', '</p>', {}),
    (114, '<ul class="list list_dot"><li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),  
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),
    (115, '<li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),  
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )
    }),
    (116, '<li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),  
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),
    (117, '<li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),  
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),
    (118, '<li>', '</li>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),  
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),
    (119, '<li>', '</li></ul>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),  
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),

    (121, '<h3>', '</h3>', {}),
    (123, '<p>', '</p>', {
        'en': (
            LIST_ITEM_HEADER_REPLS[1],
        ),  
        'es': (
            LIST_ITEM_HEADER_REPLS[1],
        )   
    }),

    (125, '<h3>', '</h3>', {}),
    (127, '<p>', '</p>', {}),

    (129, '<h3>', '</h3>', {}),
    (131, '<p>', '</p>', {}),

    (133, '<h3>', '</h3>', {}),
    (135, '<p>', '</p>', {}),

    (137, '<h3>', '</h3>', {}),
    (139, '<p>', '</p>', {}),

    (141, '<h3>', '</h3>', {}),
    (143, '<p>', '</p>', {}),

    (145, '<h3>', '</h3>', {}),
    (147, '<p>', '</p>', {}),

    (149, '<h3>', '</h3>', {}),
    (151, '<p>', '</p>', {}),

    (153, '<p>', '</p>', {
        'en': (
            (r'^(Last Updated:)', r'<strong>\1</strong>'),
        ),
        'es': (
            (r'^(Última Actualización:)', r'<strong>\1</strong>'),
        )   
    }),
)


for lang, destFilePath, lines in data:
    for command in commands:
        lineIndex, beginTag, endTag, replacements = command
        lineIndex -= 1

        for i, line in enumerate(lines):
            if i != lineIndex:
                continue

            if replacements and (lang in replacements):
                replacements = replacements[lang]

                for matchWith, replWith in replacements:
                    newLine = re.sub(matchWith, replWith, line)

                    if newLine == line:
                        raise Exception('Replacement not done {}'.format(lineIndex + 1))

                    line = newLine

            # repls...

            line = '{}{}{}'.format(beginTag, line, endTag)

            lines[i] = line

            break


    with open(destFilePath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


print(data)
