# Exercise 2. Data analysis *Python solution*
# Sasha D. Hafner

# Load modules
import numpy as np
import pandas as pd
import statsmodels.formula.api as sm
from matplotlib import pyplot as plt
from plotnine import *

# Pandas setting (will become default in some future version)
pd.options.mode.copy_on_write = True

# Load user-defined function for integration of flux
import shutil as sh
sh.copy('../functions-python/mintegrate.py', '.')
from mintegrate import mintegrate

# Read in data from csv file
dat = pd.read_csv('../data/slurry_emis.csv')

# Correct class of categorical columns
dat['gas'] = dat['gas'].astype('category')
dat['temp'] = dat['temp'].astype('category')

# Remove missing CH4 concentration values
dat = dat[dat['ch4'].notna()]

# Calculate flow rate
# cmch4 in g/m3
dat['cmch4'] = dat['ch4'] * 1.0 / 1E6 / 8.2057E-5 / (273.15 + 20)
# qch4 in g/d
#  g/d      =     g/m3     *     L/min    / L/m3 *  min/d
dat['qch4'] = dat['cmch4'] * dat['flow'] / 1000 * 1400
dat


# Get cumulative emission
# pd.DataFrame.reset_index is used just to drop some factors in the 'multi-index', as far as I can tell
# The `\` bit just allows a line break at the `.` operator
dat['ech4'] = dat.groupby(['reactor']).apply(lambda x: mintegrate(x['day'], x['qch4'], lwr = 0)).reset_index(['reactor'], drop = True)
dat

# Check days
dat[dat['day'] < 10].value_counts(['reactor', 'day'])
dat[dat['day'] > 270].value_counts(['reactor', 'day'])

# Plot
plt.scatter(dat['day'], dat['ech4'])
plt.show()
plt.close()

## Take just the total (final)
#tot = dat[dat['day'] == 283]
#tot['logemis'] = np.log10(tot['ech4'])

# Alternative for getting total 
tot = pd.DataFrame(dat.groupby(['reactor']).apply(lambda x: mintegrate(x.day, x.qch4, value = 'total')))
tot
tot.head()

# Better to get gas and temperature right in output like this
tot = pd.DataFrame(dat.groupby(['reactor', 'gas', 'temp']).apply(lambda x: mintegrate(x.day, x.qch4, value = 'total'))).reset_index()
# But it is surprisingly complicated to specify a name
tot.head()
tot.rename({0:'ech4'}, axis = 'columns', inplace = True)
tot.head()

# Get means by treatment combination
means = pd.DataFrame(tot.groupby(['gas', 'temp'])[['ech4']].mean())
stdev = pd.DataFrame(tot.groupby(['gas', 'temp'])[['ech4']].std())
means = pd.merge(means, stdev, on = ['gas', 'temp'], suffixes = ('_mean', '_sd'))
means

# Export results
tot.to_csv('../output/emis_total.csv')
dat.to_csv('../output/emis_cum.csv')
means.to_csv('../output/emis_total_means.csv')

# Plots
# Concentration values
ggplot(dat, aes('day', 'ch4', colour = 'temp', lty = 'gas', group = 'reactor')) + geom_line() + geom_point()
#plt.savefig('plots/01_measurements.png')
plt.close()

# Stats
tot['logech4'] = np.log10(tot['ech4'])
tot
tot.head()

ggplot(tot, aes('temp', 'logech4', colour = 'gas')) + geom_jitter()

# Remove background
tot = tot[tot['reactor'] != 'bg']

ggplot(tot, aes('temp', 'logech4', colour = 'gas')) + geom_jitter()

# Fit model
mod = sm.ols(formula = 'logech4 ~ gas * temp', data = tot).fit()
mod.summary()
with open('output/stats.txt', 'w') as statsfile:
    statsfile.write(mod.summary().as_text())

