import random


def randchars(n=12, chartype='alphanumeric', alphacase='both', unique=False):
    if alphacase == 'both':
        alphalist = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    elif alphacase == 'upper':
        alphalist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    elif alphacase == 'lower':
        alphalist = 'abcdefghijklmnopqrstuvwxyz'
    else:
        raise ValueError(f'alphacase "{alphacase}" not recognized')

    if chartype == 'alphanumeric':
        charlist = alphalist + '0123456789'
    elif chartype == 'alpha':
        charlist = alphalist
    elif chartype == 'numeric':
        charlist = '0123456789'
    elif chartype == 'all':
        charlist = alphalist + '0123456789' + r"""`~!@#$%^&*()_-+={}|[]\:";'<>?,./"""
    else:
        raise ValueError(f'chartype "{chartype}" not recognized')

    retval = []
    for _ in range(n):
        chosen = random.choice(charlist)
        if unique:
            charlist = charlist.replace(chosen, '')
        retval.append(chosen)
    return ''.join(retval)
