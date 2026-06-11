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
              'AJ B':['Spain','Mexico','Switzerland','Canada','Czechia','Bosnia-Herzegovina']
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

fixtures = pd.read_csv('https://dtai.cs.kuleuven.be/sports/worldcup2026/data/fixtures.csv?v=1')
preds = pd.read_json('https://dtai.cs.kuleuven.be/sports/worldcup2026/data/predictions.json?v=1').reset_index().melt(id_vars='index')
preds[['loss','tie','win','0']] = preds['value'].apply(pd.Series)
preds = preds.drop(columns=['0','value']).dropna().rename(columns={'index':'Home Team','variable':'Away Team'})
fixtures = fixtures.merge(preds,how='left')

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
standings['Proj'] = 0
standings['PPR'] = 0
standings['Points'] = 0

results = fixtures[~fixtures.Result.isna()]
planned = fixtures[fixtures.Result.isna()]
playoffs = planned[planned.Group.isna()]
planned = planned[~planned.Group.isna()]

for match in range(0,len(results)):
    temp = results.iloc[match]
    pass
    #AJ to build once result format is known

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

standings.Proj += standings.Points
standings = standings.merge(odds_group,how='left',left_on='Short',right_index=True).merge(
    odds.drop(columns=[1]).rename(columns={2:'32',3:'16',4:'QF',5:'SF',6:'Final',7:'Win'}),how='left',left_on='Short',right_index=True).fillna(0)
standings[' '] = ''

selected_standings = selections.merge(standings)

standings.to_feather('data/standings2.ftr')
selected_standings.to_feather('data/selected_standings2.ftr')