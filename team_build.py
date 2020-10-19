import pandas as pd
import numpy as np
import csv

def currencystrtofloat(amount):
    new_amount = []
    for s in amount:
        list(s)
        abbr = s[-1]
        if abbr is 'M':
            s = s[1:-1]
            s = float(''.join(s))
            s *= 1000000
        elif abbr is 'K':
            s = s[1:-1]
            s = float(''.join(s))
            s *= 1000
        else:
            s = 0
        new_amount.append(s)
    return new_amount

def data_processing(csv_path):

    df = pd.read_csv(csv_path)

    df_data = df[['ID', 'Name', 'Age', 'Nationality', 'Club', 'Photo', 'Wage', 'Value', 'Position', 'Overall']]

    # convert to float and replace euro and M and K
    df_data['Value'] = currencystrtofloat(list(df_data['Value']))

    df_data['Wage'] = currencystrtofloat(list(df_data['Wage']))

    # drop nan from Position column
    df_data = df_data.dropna(subset=['Position'])

    #remove rows with Value=0.0
    df_data = df_data[df_data['Value']!=0.0]

    #remove rows with Wage=0.0
    df_data = df_data[df_data['Wage']!=0.0]

    replace_dict = {
                    'LB':'FullBack','RB':'FullBack','LWB':'FullBack','RWB':'FullBack',
                    'CB': 'HalfBack','HBLCB':'HalfBack','RCB':'HalfBack','CDM':'HalfBack',
                    'LDM':'HalfBack','RDM':'HalfBack','CM':'HalfBack','LCM':'HalfBack','RCM':'HalfBack',
                    'LM':'HalfBack','RM':'HalfBack','CAM':'Forward','LAM':'Forward', 'RAM':'Forward', 
                    'LWF':'Forward', 'RWF':'Forward', 'CF':'Forward', 'LCF': 'Forward', 'RCF':'Forward', 
                    'GK':'GoalKeeper'
                    }

    # Mapping Position value to GoalKeeper, Forward, HalfBack, FullBack
    df_data['Position'] = df_data['Position'].replace(replace_dict)

    print(df_data.info())

    df_data.to_csv('/home/vagrant/web/fifa2019_webapp/fifa19_data.csv', quoting=csv.QUOTE_NONE, escapechar = ' ', sep='|', encoding='utf-8', 
    index=False)

    return df_data


# write_data = data_processing('/home/vagrant/web/phiture/data.csv')

def team_builder(budget, FB=2, HB=3, FR=5, GK_coef=0.05, FB_coef=0.15, HB_coef=0.30, FR_coef=0.50):

    # df = data_processing('/home/vagrant/web/phiture/data.csv')

    # df = pd.read_csv('/home/vagrant/web/fifa2019_webapp/fifa19_data.csv', sep='|')

    df = pd.read_csv('/code/fifa19_data.csv', sep='|')
    
    #split budget accordingly per position
    GK_budget = budget*GK_coef
    FB_budget = budget*FB_coef
    HB_budget = budget*HB_coef
    FR_budget = budget*FR_coef

    GK_count = 1
    FB_count = FB
    HB_count = HB+1
    FR_count = FR+1

    # print(df.info())

    # print(df.columns.tolist())
    
    keepers = df[df['Position']=='GoalKeeper'].sort_values(by='Overall', ascending=False)

    forwarders = df[df['Position']=='Forward'].sort_values(by='Overall', ascending=False)

    half_backers = df[df['Position']=='HalfBack'].sort_values(by='Overall', ascending=False)

    full_backers = df[df['Position']=='FullBack'].sort_values(by='Overall', ascending=False)

    lst_dict_keepers = keepers.to_dict('records')

    lst_dict_forwarders = forwarders.to_dict('records')

    lst_dict_half_backers = half_backers.to_dict('records')

    lst_dict_full_backers = full_backers.to_dict('records')

    #Begin building final team
    list_of_names = []
    final_team = []
    for item in lst_dict_keepers:
        if GK_count > 0 and item['Value'] <= GK_budget and item['Name'] not in list_of_names:
            item['Position'] = "GoalKeeper"
            final_team.append(item)
            list_of_names.append(item['Name'])
            GK_budget -= item['Value']
            GK_count -= 1
            FB_budget += GK_budget
    for item in lst_dict_full_backers:
        if FB_count > 0 and item['Value'] <= FB_budget/FB_count and item['Name'] not in list_of_names:
            item['Position'] = "FullBack"
            final_team.append(item)
            list_of_names.append(item['Name'])
            FB_budget -= item['Value']
            FB_count -= 1
    for item in lst_dict_half_backers:
        while HB_count == HB+1:
            HB_budget = HB_budget + FB_budget
            HB_count -= 1
        if HB_count > 0 and item['Value'] <= HB_budget/HB_count and item['Name'] not in list_of_names:
            item['Position'] = "HalfBack"
            final_team.append(item)
            list_of_names.append(item['Name'])
            HB_budget -= item['Value']
            HB_count -= 1
    for item in lst_dict_forwarders:
        while FR_count == FR+1:
            FR_budget = FR_budget + HB_budget
            FR_count -= 1
        if FR_count > 0 and item['Value'] <= FR_budget/FR_count and item['Name'] not in list_of_names:
            item['Position'] = "Forward"
            final_team.append(item)
            list_of_names.append(item['Name'])
            FR_budget -= item['Value']
            FR_count -= 1 
    leftover_budget = GK_budget + FB_budget + HB_budget + FR_budget
    if len(final_team)<1:
        print("TEAM LEN",len(final_team))
        return None
    overall_avg = round(sum([item['Overall'] for item in final_team])/len(final_team), 3)
    return dict(team=final_team, budget_left = leftover_budget, AVG_overall = overall_avg)
