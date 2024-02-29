# Python function for integration of *m*easurements
# S. Hafner

import numpy as np

def mintegrate(x, y, method = 'midpoint', lwr = float('nan'), upr = float('nan'), ylwr = 0, value = 'all'):

    if lwr != lwr:
        lwr = min(x)
    if upr != upr:
        upr = max(x)

    method = method[0]

    aaa = np.cumsum(y * (np.diff(np.append(x, upr)) / 2 + np.diff(np.append(lwr, x)) / 2))

    if value == 'all':
        return aaa
    elif value == 'total':
        return list(aaa)[-1]
    else:
        sys.exit('The "value" argument is not recognized. Use "all" to get cumulative results or else "total".')
