import pandas

def parse_population_data():
    print("Parsins xls....")
    df = pandas.read_excel('population-and-demography-copy.xlsx', skiprows=0)
    grouped_data = df.groupby(['Year', 'Continent']).apply(lambda x: x.drop(['Year', 'Continent'], axis=1).to_dict(orient='records')).reset_index(name='data')
    dict_data = grouped_data.groupby('Year').apply(lambda x: x[['Continent', 'data']].to_dict(orient='records'))

    data_new = []
    for k in dict_data.keys():

        dict_new = {'time': k, 'children' : []}
        for continent in dict_data[k]:
            continent_name = continent['Continent']
            
            continent_data = {'name' : continent_name, 'children' : []}
            
            for country_data in continent['data'] :
                country_name = country_data['Country name']
                value = country_data['Population']
                continent_data['children'].append({'name' : country_name, 'value' : value})
            
            dict_new['children'].append(continent_data)
        data_new.append(dict_new)
    
    return data_new