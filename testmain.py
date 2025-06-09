import data.read_data as rd
import pandas as pd

df = pd.DataFrame(rd.get_runner_data())

print(df)
