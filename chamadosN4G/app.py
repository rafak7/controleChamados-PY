from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)


# Função para carregar dados do CSV
def carregar_dados(file_path):
    df = pd.read_csv(file_path, delimiter=';')
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y %H:%M:%S')
    df['Duracao'] = pd.to_timedelta(df['Duracao'].str.strip('"'))

    def classificar_turno(horario):
        if 8 <= horario.hour < 13:
            return 'Manhã'
        elif 13 <= horario.hour < 18:
            return 'Tarde'
        elif 18 <= horario.hour < 24:
            return 'Noite'
        else:
            return 'Madrugada'

    df['Turno'] = df['Data'].apply(classificar_turno)
    return df


# Função para formatar a duração média em minutos e segundos
def formatar_duracao(duracao):
    minutos, segundos = divmod(duracao.seconds, 60)
    return f"{minutos}m {segundos}s"


# Caminho para o arquivo CSV combinado
csv_file_path = 'combined_extrato.csv'
df = carregar_dados(csv_file_path)


@app.route('/', methods=['GET', 'POST'])
def index():
    df_filtrado = pd.DataFrame()
    turno_status_percent = pd.DataFrame()
    turno_status_count = pd.DataFrame()
    total_chamadas_por_turno = pd.Series()
    duração_media_por_turno = pd.Series()
    duração_total_por_turno = pd.Series()
    numero_mais_frequente = None
    chamadas_numero_mais_frequente = None
    status_options = df['Status'].unique()

    if request.method == 'POST':
        datas_selecionadas = request.form.get('datas')
        status_selecionado = request.form.get('status')

        if datas_selecionadas:
            data_inicio, data_fim = datas_selecionadas.split(' - ')
            data_inicio = pd.to_datetime(data_inicio)
            data_fim = pd.to_datetime(data_fim)
            df_filtrado = df[(df['Data'] >= data_inicio) & (df['Data'] <= data_fim)]
        else:
            df_filtrado = df.copy()

        if status_selecionado and status_selecionado != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Status'] == status_selecionado]

        if not df_filtrado.empty:
            turno_status_percent = df_filtrado.groupby('Turno')['Status'].value_counts(normalize=True).unstack() * 100
            turno_status_count = df_filtrado.groupby('Turno')['Status'].value_counts().unstack()
            total_chamadas_por_turno = df_filtrado['Turno'].value_counts()
            duração_media_por_turno = df_filtrado.groupby('Turno')['Duracao'].mean().apply(formatar_duracao)
            duração_total_por_turno = df_filtrado.groupby('Turno')['Duracao'].sum()
            numero_mais_frequente = df_filtrado['De'].value_counts().idxmax()
            chamadas_numero_mais_frequente = df_filtrado['De'].value_counts().max()

    return render_template('index.html',
                           data=df_filtrado.to_dict(orient='records') if not df_filtrado.empty else [],
                           turno_status_percent=turno_status_percent.round(2),
                           turno_status_count=turno_status_count,
                           total_chamadas_por_turno=total_chamadas_por_turno,
                           duração_media_por_turno=duração_media_por_turno,
                           duração_total_por_turno=duração_total_por_turno,
                           numero_mais_frequente=numero_mais_frequente,
                           chamadas_numero_mais_frequente=chamadas_numero_mais_frequente,
                           status_options=status_options)


if __name__ == '__main__':
    app.run(debug=True)
