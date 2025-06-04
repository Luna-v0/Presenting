def p_f1(regras):
    """
    S : numero '+' S
    """
    regras[0] = regras[1] + regras[3]


def p_f2(regras):
    """
    S : numero
    """
    regras[0] = regras[1]
