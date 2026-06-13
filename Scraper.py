import pandas as pd

selections = {'Steph S':['France','Colombia','Australia','Canada','South Africa','Saudi Arabia'],
              'Nick P':['Spain','Germany','Japan','Norway','Czechia','Ghana'],
              'Ian C':['France','Belgium','Switzerland','Canada','Czechia','Bosnia-Herzegovina'],
              'Yasmin S':['Argentina','Germany','Japan','Norway','Scotland','Ghana'],
              'Gavin F':['Argentina','Belgium','Ecuador','Canada','Scotland','Ghana'],
              'Matt C':['France','Germany','Turkey','Norway','Czechia','Bosnia-Herzegovina'],
              'Tim C':['France','Germany','Japan','Norway','Czechia','Bosnia-Herzegovina'],
              'Geoff T':['France','Germany','Switzerland','Norway','Scotland','Saudi Arabia'],
              'Caity H':['France','Mexico','Australia','Ivory Coast','South Africa','Ghana'],
              'Laura B':['Spain','Belgium','Switzerland','Norway','Scotland','Ghana'],
              'Jessie DB':['France','Germany','Iran','Norway','Tunisia','Curaçao'],
              'AJ B':['Spain','Mexico','Switzerland','Canada','Czechia','Bosnia-Herzegovina'],
              'Anita VR':['Brazil','Croatia','Ecuador','Ivory Coast','South Africa','Bosnia-Herzegovina'],
              'Matt D':['Spain','Germany','Japan','Canada','Czechia','Ghana'],
              'Adrian S':['France','Belgium','Japan','Canada','Tunisia','Ghana']}
selections = pd.DataFrame(selections).T
selections = selections.reset_index().rename(columns={'index':'Person'}).melt(id_vars='Person',var_name='pot',value_name='Country')
selections.pot += 1
selections = selections.merge(selections.groupby('Country').Person.count().reset_index().rename(columns={'Person':'Count'}))
selections['Uniqueness'] = 1 - (selections['Count'] - 1) / (selections.Person.nunique() - 1)

groups = {'A':['MEX','RSA','KOR','CZE'],
          'B':['CAN','BIH','QAT','SUI'],
          'C':['BRA','MAR','HAI','SCO'],
          'D':['USA','PAR','AUS','TUR'],
          'E':['GER','CUW','CIV','ECU'],
          'F':['NED','JPN','SWE','TUN'],
          'G':['BEL','EGY','IRN','NZL'],
          'H':['ESP','CPV','KSA','URU'],
          'I':['FRA','SEN','IRQ','NOR'],
          'J':['ARG','ALG','AUT','JOR'],
          'K':['POR','COD','UZB','COL'],
          'L':['ENG','CRO','GHA','PAN']}

names = {'MEX':'Mexico','RSA':'South Africa','KOR':'South Korea','CZE':'Czechia',
         'CAN':'Canada','BIH':'Bosnia-Herzegovina','QAT':'Qatar','SUI':'Switzerland',
         'BRA':'Brazil','MAR':'Morocco','HAI':'Haiti','SCO':'Scotland',
         'USA':'United States','PAR':'Paraguay','AUS':'Australia','TUR':'Turkey',
         'GER':'Germany','CUW':'Curaçao','CIV':'Ivory Coast','ECU':'Ecuador',
         'NED':'Netherlands','JPN':'Japan','SWE':'Sweden','TUN':'Tunisia',
         'BEL':'Belgium','EGY':'Egypt','IRN':'Iran','NZL':'New Zealand',
         'ESP':'Spain','CPV':'Cape Verde Islands','KSA':'Saudi Arabia','URU':'Uruguay',
         'FRA':'France','SEN':'Senegal','IRQ':'Iraq','NOR':'Norway',
         'ARG':'Argentina','ALG':'Algeria','AUT':'Austria','JOR':'Jordan',
         'POR':'Portugal','COD':'Congo DR','UZB':'Uzbekistan','COL':'Colombia',
         'ENG':'England','CRO':'Croatia','GHA':'Ghana','PAN':'Panama'}

groups = pd.DataFrame(groups).T.reset_index().rename(columns={'index':'Group'}).melt(id_vars='Group',value_name='Short').drop(columns='variable')
groups['Country'] = groups.Short.replace(names)

import requests

API_KEY = "1d042d223fa447cf863e6e820aa3d96a"

r = requests.get(
    "https://api.football-data.org/v4/competitions/WC/matches",
    headers={"X-Auth-Token": API_KEY})

matches = []
for i in range(0,len(r.json()['matches'])):
    temp = r.json()['matches'][i]
    date = temp['utcDate']
    stage = temp['stage']
    home_team = temp['homeTeam']['name']
    away_team = temp['awayTeam']['name']
    home_score = temp['score']['fullTime']['home']
    away_score = temp['score']['fullTime']['away']
    matches.append([date,stage,home_team,away_team,home_score,away_score])
matches = pd.DataFrame(matches,columns=['Date','Stage','Home','Away','Home_Score','Away_Score'])
matches.iloc[0].Home_Score = 3
matches.iloc[0].Away_Score = 1
matches['Home_Win'] = (matches.Home_Score > matches.Away_Score).astype('int')
matches['Away_Win'] = (matches.Home_Score < matches.Away_Score).astype('int')
matches['Draw'] = (matches.Home_Score == matches.Away_Score).astype('int')
matches.Home = matches.Home.replace({v: k for k, v in names.items()})
matches.Away = matches.Away.replace({v: k for k, v in names.items()})
matches_regular = matches[matches.Stage == 'GROUP_STAGE']
matches_playoff = matches[matches.Stage != 'GROUP_STAGE']

fixtures = pd.read_csv('https://dtai.cs.kuleuven.be/sports/worldcup2026/data/fixtures.csv?v=1')
preds = pd.read_json('https://dtai.cs.kuleuven.be/sports/worldcup2026/data/predictions.json?v=1').reset_index().melt(id_vars='index')
preds[['loss','tie','win','0']] = preds['value'].apply(pd.Series)
preds = preds.drop(columns=['0','value']).dropna().rename(columns={'index':'Home Team','variable':'Away Team'})
fixtures = fixtures.merge(preds,how='left')
fixtures = fixtures.merge(matches.rename(columns={'Home':'Home Team','Away':'Away Team'})[['Home Team','Away Team','Home_Score','Away_Score','Home_Win','Away_Win','Draw']],how='left')
fixtures.loc[~fixtures.Home_Score.isna(),'Result'] = 1

paths = pd.read_json('https://dtai.cs.kuleuven.be/sports/worldcup2026/data/data.json?v=1')
odds = []

for i in range(0,len(paths)):
    temp = paths.iloc[i]
    temp_team = temp['name']
    temp_paths = temp.paths
    for j in range(0,len(temp_paths)):
        temp_path = temp_paths[j]
        temp_path_level = len(temp_path['pos_path'])
        temp_path_probability = temp_path['probability']
        if (temp_path_level == 1) & (temp_path['pos_path'][0].endswith('1')):
            odds.append([temp_team,'1st',temp_path_probability])   
        if (temp_path_level == 1) & (temp_path['pos_path'][0].endswith('2')):
            odds.append([temp_team,'2nd',temp_path_probability])   
        if (temp_path_level == 1) & (temp_path['pos_path'][0].endswith('3')):
            odds.append([temp_team,'3rd',temp_path_probability])        
        if (temp_path_level == 1) & (temp_path['pos_path'][0].endswith('4')):
            odds.append([temp_team,'4th',temp_path_probability])
        odds.append([temp_team,temp_path_level,temp_path_probability])
odds = pd.DataFrame(odds,columns=['country','level','odds'])
odds = odds.groupby(['country','level']).agg({'odds':'sum'}).reset_index().pivot(index='country',columns='level',values='odds').fillna(0)
odds_group = odds[['1st','2nd','3rd','4th']]
odds = odds.drop(columns=odds_group.columns)

standings = groups.copy(True)
standings['W'] = 0
standings['D'] = 0
standings['L'] = 0
standings['GF'] = 0
standings['GA'] = 0
standings['GD'] = 0
standings['Proj'] = 0.0
standings['PPR'] = 0
standings['Points'] = 0

results = fixtures[~fixtures.Result.isna()]
planned = fixtures[fixtures.Result.isna()]
playoffs = planned[planned.Group.isna()]
planned = planned[~planned.Group.isna()]

for match in range(0,len(results)):
    temp = results.iloc[match]
    standings.loc[standings.Short == temp['Home Team'],'W'] = standings.W + temp.Home_Win
    standings.loc[standings.Short == temp['Home Team'],'D'] = standings.D + temp.Draw
    standings.loc[standings.Short == temp['Home Team'],'L'] = standings.L + temp.Away_Win
    standings.loc[standings.Short == temp['Home Team'],'GF'] = standings.GF + temp.Home_Score
    standings.loc[standings.Short == temp['Home Team'],'GA'] = standings.GA + temp.Away_Score
    standings.loc[standings.Short == temp['Home Team'],'PointsbyMatch'] = standings.PointsbyMatch.apply(lambda lst: lst + [temp.Home_Win * 3 + temp.Draw])

    standings.loc[standings.Short == temp['Away Team'],'W'] = standings.W + temp.Away_Win
    standings.loc[standings.Short == temp['Away Team'],'D'] = standings.D + temp.Draw
    standings.loc[standings.Short == temp['Away Team'],'L'] = standings.L + temp.Home_Win
    standings.loc[standings.Short == temp['Away Team'],'GF'] = standings.GF + temp.Away_Score
    standings.loc[standings.Short == temp['Away Team'],'GA'] = standings.GA + temp.Home_Score
    standings.loc[standings.Short == temp['Away Team'],'PointsbyMatch'] = standings.PointsbyMatch.apply(lambda lst: lst + [temp.Away_Win * 3 + temp.Draw])

    standings.loc[(standings.Short != temp['Home Team']) & (standings.Short != temp['Away Team']),'PointsbyMatch'] = standings.PointsbyMatch.apply(lambda lst: lst + [0])

for match in range(0,len(planned)):
    temp = planned.iloc[match]
    standings.loc[standings.Short == temp['Home Team'],'Proj'] = standings.Proj + temp.win * 3 + temp.tie
    standings.loc[standings.Short == temp['Away Team'],'Proj'] = standings.Proj + temp.loss * 3 + temp.tie
    standings.loc[standings.Short == temp['Home Team'],'PPR'] = standings.PPR + 3
    standings.loc[standings.Short == temp['Away Team'],'PPR'] = standings.PPR + 3

for team in range(0,len(odds)):
    temp = odds.iloc[team]
    standings.loc[standings.Short == temp.name,'Proj'] = standings.Proj + temp[[3,4,5,6,7]].sum() * 5
    if standings[standings.Short == temp.name].PPR.values[0] > 0:
        standings.loc[standings.Short == temp.name,'PPR'] = standings.PPR + 25
    else:
        standings.loc[standings.Short == temp.name,'PPR'] = standings.PPR + (len(temp[temp > 0]) - len(temp[temp >= 1]) - 1) * 5
        #AJ to check once in knockouts but this should work

standings.GD = standings.GF - standings.GA
standings.Points = standings.W * 3 + standings.D * 1
standings.Proj += standings.Points
standings.PPR += standings.Points
standings = standings.merge(odds_group,how='left',left_on='Short',right_index=True).merge(
    odds.drop(columns=[1]).rename(columns={2:'32',3:'16',4:'QF',5:'SF',6:'Final',7:'Win'}),how='left',left_on='Short',right_index=True).fillna(0)
standings[' '] = ''

selected_standings = selections.merge(standings)

standings.to_feather('data/standings.ftr')
selected_standings.to_feather('data/selected_standings.ftr')