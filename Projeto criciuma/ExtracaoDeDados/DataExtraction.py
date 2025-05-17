#esse é o codigo que eu uso pra extrair as informações dos jogos do criciuma de forma autoamtica

import requests
import pandas as pd
from datetime import datetime
 #coloca as suas keys aqui
API_FOOTBALL_KEY = 'key da api' #https://dashboard.api-football.com
WEATHER_API_KEY = 'key da api' #https://www.visualcrossing.com/account/

headers = {
    'x-apisports-key': API_FOOTBALL_KEY
}

seasons = [2021, 2022, 2023] #a api que eu to usando só vai eté 2023, se quiser as temporadas mais recentes precisa de plano premium
todos_jogos = []
 #só da pra pegar uma season por vez porque o argumento de season do request da api é obrigatorio e aceita só um parametro
 #então eu coloquei em uma estrutura de repetição pra pegar de todas as temporadas que eu quiser
for season in seasons:
    print(f"Buscando jogos da season {season}...")
    response = requests.get(
        'https://v3.football.api-sports.io/fixtures',
        headers=headers,
        params={
            'season': season,
            'team': 140, #o id 140 é o id referente ao criciuma na api
            'timezone': 'America/Sao_Paulo' #pra ajustar o horario da partida pro fuso horario do brasil no registro
        }
    )
    data = response.json()
    jogos = data.get('response', [])
    print(f"  ✅ Jogos encontrados na temporada {season}: {len(jogos)}")

    for jogo in jogos:
        fixture = jogo['fixture']
        teams = jogo['teams']
        venue = fixture.get('venue', {})
        date_str = fixture['date']
        data_jogo = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        data_formatada = data_jogo.strftime('%Y-%m-%d')

        cidade = venue.get('city') or "Criciúma"
        
        # não consegui encontrar uma forma de conseguir o clima dos estadios na documentação da api_sports então usei uma api separada
        #usa a 'data_formatada' para pegar o dia do
        weather_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{cidade}/{data_formatada}?key={WEATHER_API_KEY}&unitGroup=metric&include=days"

        try:
            clima_resp = requests.get(weather_url)
            clima_data = clima_resp.json()
            dia_clima = clima_data['days'][0]
            temperatura = dia_clima.get('temp')
            umidade = dia_clima.get('humidity')
            condicao = dia_clima.get('conditions')
        except Exception:
            temperatura = umidade = condicao = 'Não disponível'

        status_jogo = fixture['status']['long']
        gols_casa = jogo['goals']['home']
        gols_fora = jogo['goals']['away']
        time_casa = teams['home']['id']
        time_visitante = teams['away']['id']
        time_criciuma = 140
        #verifica qual time venceu
        if time_casa == time_criciuma and gols_casa > gols_fora:
            venceu = "sim"
        elif time_visitante == time_criciuma and gols_fora > gols_casa:
            venceu = "sim"
        else:
            venceu = "nao"
        #coloca o jogo na lista com todos os jogos
        todos_jogos.append({
            'Season': season,
            'Data': data_formatada,
            'Competição': jogo['league']['name'],
            'Rodada': jogo['league']['round'],
            'Time Casa': teams['home']['name'],
            'Time Visitante': teams['away']['name'],
            'Estádio': venue.get('name', 'Desconhecido'),
            'Cidade': cidade,
            'Temperatura (°C)': temperatura,
            'Umidade (%)': umidade,
            'Condição do Tempo': condicao,
            'Placar': f"{gols_casa} x {gols_fora}",
            'Status': status_jogo,
            'Partida Vencida?': venceu
        })

df = pd.DataFrame(todos_jogos)
df.to_excel("ExtracaoDeDados\criciuma2021_2023.xlsx", index=False)

print("✅ Arquivo 'criciuma2021_2023' criado com sucesso!")
