import pandas as pd

selections = {'Steph N':['Spain','Germany','Switzerland','Norway','Czechia','Bosnia-Herzegovina'],
              'Kyle W':['Portugal','United States','Turkey','Panama','Czechia','New Zealand'],
              'Melanie D':['Spain','Germany','Switzerland','Norway','Scotland','Ghana'],
              'Amy A':['Spain','Germany','Japan','Canada','Czechia','New Zealand'],
              'Elissa K':['Netherlands','Belgium','Switzerland','Norway','South Africa','New Zealand'],
              'James K':['Portugal','Germany','Austria','Sweden','Scotland','New Zealand'],
              'Victor T':['Argentina','Colombia','Turkey','Norway','Scotland','Ghana'],
              'Matt M':['Spain','Mexico','Turkey','Norway','Czechia','Bosnia-Herzegovina'],
              'David H':['France','Belgium','South Korea','Paraguay','Tunisia','Saudi Arabia'],
              'Nicole G':['England','Germany','Switzerland','Norway','Czechia','Ghana'],
              'Agustin D':['Argentina','Germany','Japan','Canada','Scotland','Bosnia-Herzegovina'],
              'Mika S':['Argentina','Belgium','Japan','Canada','Tunisia','New Zealand'],
              'AJ B':['Spain','Mexico','Switzerland','Canada','Czechia','Bosnia-Herzegovina'],
              'Rania C':['Spain','Colombia','Japan','Ivory Coast','Scotland','Saudi Arabia'],
              'Ovidiu C':['Brazil','Germany','Austria','Sweden','Scotland','Bosnia-Herzegovina'],
              'Marcelo K':['France','Germany','Switzerland','Paraguay','Scotland','New Zealand'],
              'Saloni G':['Spain','Germany','Japan','Norway','Scotland','Ghana'],
              'Ayrton FdS':['Argentina','Croatia','Japan','Sweden','Scotland','Ghana'],
              'Patricia R':['Portugal','Germany','Australia','Paraguay','Czechia','New Zealand'],
              'Kirby L':['Spain','Germany','Japan','Sweden','Scotland','New Zealand'],
              'Raphael dA':['Brazil','Colombia','Ecuador','Norway','Congo DR','Curaçao'],
              'Andrew P':['England','Colombia','Switzerland','Paraguay','Scotland','Ghana'],
              'Miranda H':['France','Germany','Japan','Norway','Czechia','Ghana'],
              'Ana dA':['Spain','Germany','Switzerland','Canada','Uzbekistan','Ghana']
              }
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
matches.Home = matches.Home.replace({v: k for k, v in names.items()})
matches.Away = matches.Away.replace({v: k for k, v in names.items()})
matches['key'] = matches.dropna(subset=['Home','Away']).apply(lambda r: tuple(sorted([r['Home'], r['Away']])),axis=1)#
matches['unsort_key'] = matches.dropna(subset=['Home']).apply(lambda r: tuple(([r['Home'], r['Away']])),axis=1)#
mask = matches.key != matches.unsort_key
matches.loc[mask, ['Home_Score', 'Away_Score']] = (matches.loc[mask, ['Away_Score', 'Home_Score']].values)
matches['Home_Win'] = (matches.Home_Score > matches.Away_Score).astype('int')
matches['Away_Win'] = (matches.Home_Score < matches.Away_Score).astype('int')
matches['Draw'] = (matches.Home_Score == matches.Away_Score).astype('int')
matches_regular = matches[matches.Stage == 'GROUP_STAGE']
matches_playoff = matches[matches.Stage != 'GROUP_STAGE']

fixtures = pd.read_csv('https://dtai.cs.kuleuven.be/sports/worldcup2026/data/fixtures.csv?v=1')
fixtures['key'] = fixtures.apply(lambda r: tuple(sorted([r['Home Team'], r['Away Team']])),axis=1) #
preds = pd.read_json('https://dtai.cs.kuleuven.be/sports/worldcup2026/data/predictions.json?v=1').reset_index().melt(id_vars='index')
preds[['loss','tie','win','0']] = preds['value'].apply(pd.Series)
preds = preds.drop(columns=['0','value']).dropna().rename(columns={'index':'Home Team','variable':'Away Team'})
fixtures = fixtures.merge(preds,how='left')
fixtures = fixtures.merge(matches.rename(columns={'Home':'Home Team','Away':'Away Team'})[['key','Home_Score','Away_Score',
                                                                                           'Home_Win','Away_Win','Draw']],how='left',on='key') #
fixtures.loc[~fixtures.Home_Score.isna(),'Result'] = 1
fixtures['Home Team'], fixtures['Away Team'] = zip(*fixtures['key'])

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
odds = [['ALG',0.000,0.000,0.000,0.000,0.000],
        ['ARG',1.000,0.909,0.589,0.384,0.216],
        ['AUS',0.000,0.000,0.000,0.000,0.000],
        ['AUT',0.000,0.000,0.000,0.000,0.000],
        ['BEL',1.000,0.498,0.146,0.053,0.019],
        ['BIH',0.000,0.000,0.000,0.000,0.000],
        ['BRA',1.000,0.711,0.409,0.191,0.089],
        ['CAN',1.000,0.000,0.000,0.000,0.000],
        ['CPV',0.000,0.000,0.000,0.000,0.000],
        ['COL',1.000,0.635,0.289,0.151,0.062],
        ['CRO',0.000,0.000,0.000,0.000,0.000],
        ['COD',0.000,0.000,0.000,0.000,0.000],
        ['ECU',0.000,0.000,0.000,0.000,0.000],
        ['EGY',1.000,0.091,0.020,0.004,0.001],
        ['ENG',1.000,0.505,0.268,0.122,0.054],
        ['FRA',1.000,1.000,0.678,0.361,0.201],
        ['GER',0.000,0.000,0.000,0.000,0.000],
        ['GHA',0.000,0.000,0.000,0.000,0.000],
        ['CIV',0.000,0.000,0.000,0.000,0.000],
        ['JAP',0.000,0.000,0.000,0.000,0.000],
        ['MEX',1.000,0.495,0.196,0.068,0.020],
        ['MAR',1.000,1.000,0.322,0.118,0.045],
        ['NED',0.000,0.000,0.000,0.000,0.000],
        ['NOR',1.000,0.289,0.127,0.038,0.010],
        ['PAR',1.000,0.000,0.000,0.000,0.000],
        ['POR',1.000,0.293,0.175,0.078,0.034],
        ['SEN',0.000,0.000,0.000,0.000,0.000],
        ['ESP',1.000,0.707,0.555,0.353,0.223],
        ['KSA',0.000,0.000,0.000,0.000,0.000],
        ['SWE',0.000,0.000,0.000,0.000,0.000],
        ['SUI',1.000,0.365,0.103,0.042,0.014],
        ['USA',1.000,0.502,0.124,0.038,0.013]]

odds = pd.DataFrame(odds,columns=['country',3,4,5,6,7]).set_index('country')
odds[2] = 1
odds = odds[[2,3,4,5,6,7]]

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
standings['PointsbyMatch'] = [[]]*len(standings)

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
    pts = ((temp[[3,4,5,6,7]] == 1).astype('int') * 5).sum()
    proj = ((temp[[3,4,5,6,7]] * 5)).sum() - pts
    ppr = ((temp[[3,4,5,6,7]] > 0).astype('int') * 5).sum() - pts
    standings.loc[standings.Short == temp.name,'Points'] = standings.Points + pts
    standings.loc[standings.Short == temp.name,'Proj'] = standings.Proj + proj
    standings.loc[standings.Short == temp.name,'PPR'] = standings.PPR + ppr
    standings.loc[standings.Short == temp.name, 'PointsbyMatch'] = standings.loc[standings.Short == temp.name, 'PointsbyMatch'].apply(lambda lst: lst + ((temp[[3,4,5,6,7]] == 1).astype(int) * 5).tolist())

standings.GD = standings.GF - standings.GA
standings.Points = standings.W * 3 + standings.D * 1 + standings.Points
standings.Proj += standings.Points
standings.PPR += standings.Points
standings = standings.merge(odds_group,how='left',left_on='Short',right_index=True).merge(
    odds.rename(columns={2:'32',3:'16',4:'QF',5:'SF',6:'Final',7:'Win'}),how='left',left_on='Short',right_index=True).fillna(0)
#standings = standings.merge(odds_group,how='left',left_on='Short',right_index=True).merge(
#    odds.drop(columns=[1]).rename(columns={2:'32',3:'16',4:'QF',5:'SF',6:'Final',7:'Win'}),how='left',left_on='Short',right_index=True).fillna(0)
standings[' '] = ''

selected_standings = selections.merge(standings)

standings.to_feather('data/standings2.ftr')
selected_standings.to_feather('data/selected_standings2.ftr')