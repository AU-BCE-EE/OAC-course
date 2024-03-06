# Exercise 1. Data manipulation *Python solution*
# Sasha D. Hafner

# 1. Read in data
import pandas as pd
#air = pd.read_csv('../data/air_cleaners.csv')
air = pd.read_csv('../data/air_cleaners.csv', parse_dates = ['timestamp'])
air

# 2. Check data
# Missing values
air.isnull().sum()

# Min/max etc.
air.describe()
air.describe().transpose()

# More
air.size
air.shape
air.ndim

# 3. Subset
ns = air[air['aircleaner'] == 'NoSmell4.2']
air.shape
ns.shape
ns

tol = air[(air['aircleaner'] == 'NoSmell4.2') & (air['compound_name'] == 'Toluene') & (air['flow_dir'] == 'In')]
print(tol.shape)
print(tol)

# 4. Merge
mm = pd.read_csv('../data/mol_mass.csv')
print(mm.shape)
mm

print(air.shape)
air = pd.merge(air, mm, on = 'form')
print(air.shape)
print(air)
air

# 5. Add columns
air['concm'] = air['mol_mass'] * 1.0 * air['concentration'] / 1E9 / 8.2057E-5 / (273.15 + 20)
air

# Need to add different flow rates depending on air cleaner model
airflow = pd.DataFrame({'aircleaner': ['PureAir2000', 'NoSmell4.2'], 'air_flow': [0.13, 0.1]})
airflow

air = pd.merge(air, airflow, on = 'aircleaner')
air

# In g/min.
air
air['mass_flow'] = air['concm'] * air['air_flow']
print(air)

# 6. Dates and times
import datetime as dt

print(air.dtypes)

#air = pd.read_csv('../../data/air_cleaners.csv', parse_dates = ['timestamp'])

print(air.dtypes)
print(air)

air['etime_min'] = (air['timestamp'] - pd.to_datetime('03/10/2022 13:40')).dt.total_seconds() / 60
print(air)

# 7. Grouped operations
summ_mean = air.groupby(['aircleaner', 'flow_dir', 'compound_name'])['concentration'].mean()
summ_sd = air.groupby(['aircleaner', 'flow_dir', 'compound_name'])['concentration'].std()
print(summ_mean)
print(summ_sd)

summ = pd.merge(summ_mean, summ_sd, on = ['aircleaner', 'flow_dir', 'compound_name'])
print(summ)
summ = summ.reset_index()
print(summ)

# 8. Export
summ.to_csv('output/cleaner_summary.csv')

# 9. Integrate
import shutil as sh
sh.copy('../../python-functions/mintegrate.py', '.')
from mintegrate import mintegrate

print(air)
air['mass_cum'] = air.groupby(['aircleaner', 'flow_dir', 'compound_name']).apply(lambda x: mintegrate(x['etime_min'], x['mass_flow'])).reset_index(['aircleaner', 'flow_dir', 'compound_name'], drop = True)
print(air)

airtot = air.groupby(['aircleaner', 'flow_dir', 'compound_name']).apply(lambda x: mintegrate(x['etime_min'], x['mass_flow'], value = 'total')).reset_index(name = 'mass_tot')
print(airtot)

# 10. Reshape
airw = airtot.pivot_table(index = ['aircleaner', 'compound_name'], columns = ['flow_dir'], values = ['mass_tot']).reset_index()
print(airw)

print(airw.keys)
airw['rem_eff'] = 100 * (1 - airw['mass_tot']['Out'] / airw['mass_tot']['In'])
print(airw)

