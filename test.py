import pandas as pd

pd.set_option('display.max_rows', None)

m1500 = pd.read_csv('./ncaa-results/Mens-1500-Meters.csv')
print(m1500)