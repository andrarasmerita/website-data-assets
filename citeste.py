import pandas as pd

tabel = pd.read_parquet("data/domenii.parquet")
domenii = tabel["root_domain"].dropna().str.strip().tolist()

with open("data/domains.txt", "w", encoding="utf-8") as fisier:
    fisier.write("\n".join(domenii))

print(len(domenii), "domenii salvate")