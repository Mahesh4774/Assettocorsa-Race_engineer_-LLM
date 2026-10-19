import csv
import pandas as pd

def car_camber(filename):
    with open(filename) as f:
        skp_row = 0
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if row and row[0] == "time":
                skp_row = i
                break

    df = pd.read_csv(filename, skiprows=skp_row, low_memory=False)
    df = df.drop(index=0).reset_index(drop=True)

    camber_ls = [col for col in df.columns if 'Camber' in col]
    df[camber_ls] = df[camber_ls].apply(pd.to_numeric, errors='coerce').ffill()

    df['distance_m'] = pd.to_numeric(df['Lap Distance'], errors='coerce').ffill()

    return df[camber_ls], df['distance_m']

camber_a, lapdist_a = car_camber("12102026-213648-Moota47-bny_porsche_992_gt3r-ks_nordschleife-nordschleife-raw.csv")
print(camber_a.head(10))
print(lapdist_a[1000:2000])
