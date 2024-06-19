import os
import pandas as pd

csv_files_dir = 'csv_files'
combined_csv_path = 'combined_extrato.csv'

# Listar arquivos CSV no diretório
csv_files = [f for f in os.listdir(csv_files_dir) if f.endswith('.csv')]

# Combinar todos os arquivos CSV em um único DataFrame
combined_df = pd.concat([pd.read_csv(os.path.join(csv_files_dir, f), delimiter=';') for f in csv_files])

# Salvar o DataFrame combinado em um novo arquivo CSV
combined_df.to_csv(combined_csv_path, index=False, sep=';')
