import pandas
import pymongo 
import copy 

continent_hierarchy =  {"Africa": { \
    "Northern Africa": ["Algeria", "Egypt", "Libya", "Morocco", "Western Sahara"],\
    "Western Africa": ["Benin", "Burkina Faso", "Cape Verde", "Cote d'Ivoire", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Liberia", "Mali", "Mauritania", "Niger", "Nigeria", "Saint Helena", "Senegal", "Sierra Leone", "Togo"],\
    "Middle Africa": ["Angola", "Cameroon", "Central African Republic", "Chad", "Congo", "Democratic Republic of Congo", "Equatorial Guinea", "Gabon", "Sao Tome and Principe"],\
    "Eastern Africa": ["Burundi", "Comoros", "Djibouti", "Eritrea", "Ethiopia", "Kenya", "Madagascar", "Malawi", "Mauritius", "Mayotte", "Mozambique", "Reunion", "Rwanda", "Seychelles", "Somalia", "South Sudan", "Tanzania", "Uganda", "Zambia", "Zimbabwe"],\
    "Southern Africa": ["Botswana", "Eswatini", "Lesotho", "Namibia", "South Africa"]\
  },\
  "Americas": {\
    "Northern America": ["Canada", "Greenland"],\
    "Caribbean": ["Anguilla", "Antigua and Barbuda", "Aruba", "Bahamas", "Barbados", "Bermuda", "Bonaire Sint Eustatius and Saba", "British Virgin Islands", "Cayman Islands", "Cuba", "Curacao", "Dominica", "Dominican Republic", "Grenada", "Guadeloupe", "Haiti", "Jamaica", "Martinique", "Montserrat", "Puerto Rico", "Saint Barthelemy", "Saint Kitts and Nevis", "Saint Lucia", "Saint Martin (French part)", "Saint Vincent and the Grenadines", "Sint Maarten (Dutch part)", "Trinidad and Tobago", "Turks and Caicos Islands", "United States Virgin Islands"],\
    "Central America": ["Belize", "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Mexico", "Nicaragua", "Panama"],\
    "South America": ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Falkland Islands", "French Guiana", "Guyana", "Paraguay", "Peru", "Suriname", "Uruguay", "Venezuela"]\
  },\
  "Asia": {\
    "Central Asia": ["Kazakhstan", "Kyrgyzstan", "Tajikistan", "Turkmenistan", "Uzbekistan"],\
    "Eastern Asia": ["China", "Hong Kong", "Japan", "North Korea", "South Korea", "Macao", "Mongolia", "Taiwan"],\
    "South-Eastern Asia": ["Brunei", "Cambodia", "Indonesia", "Laos", "Malaysia", "Myanmar", "Philippines", "Singapore", "Thailand", "Timor", "Vietnam"],\
    "Southern Asia": ["Afghanistan", "Bangladesh", "Bhutan", "India", "Iran", "Maldives", "Nepal", "Pakistan", "Sri Lanka"],\
    "Western Asia": ["Armenia", "Azerbaijan", "Bahrain", "Cyprus", "Georgia", "Iraq", "Israel", "Jordan", "Kuwait", "Lebanon", "Oman", "Palestine", "Qatar", "Saudi Arabia", "Syria", "Turkey", "United Arab Emirates", "Yemen"]\
  },\
  "Europe": {\
    "Eastern Europe": ["Belarus", "Bulgaria", "Czechia", "Hungary", "Moldova", "Poland", "Romania", "Russia", "Slovakia", "Ukraine"],\
    "Northern Europe": ["Denmark", "Estonia", "Faroe Islands", "Finland", "Guernsey", "Iceland", "Ireland", "Isle of Man", "Jersey", "Latvia", "Lithuania", "Norway", "Sweden", "United Kingdom"],\
    "Southern Europe": ["Albania", "Andorra", "Bosnia and Herzegovina", "Croatia", "Gibraltar", "Greece", "Italy", "Kosovo", "Malta", "Montenegro", "North Macedonia", "Portugal", "San Marino", "Serbia", "Slovenia", "Spain"],\
    "Western Europe": ["Austria", "Belgium", "France", "Germany", "Liechtenstein", "Luxembourg", "Monaco", "Netherlands", "Switzerland"]\
  },\
  "Oceania": {
    "Australia and New Zealand": ["Australia", "New Zealand"],\
    "Melanesia": ["Fiji", "New Caledonia", "Papua New Guinea", "Solomon Islands", "Vanuatu"],\
    "Micronesia": ["Guam", "Kiribati", "Marshall Islands", "Micronesia (country)", "Nauru", "Northern Mariana Islands", "Palau"],\
    "Polynesia": ["American Samoa", "Cook Islands", "French Polynesia", "Niue", "Samoa", "Tonga", "Tuvalu", "Wallis and Futuna"]\
  }}





def parse_population_data_2():
    continent_hierarchy1 = copy.deepcopy(continent_hierarchy)
    continent_hierarchy1["Americas"]["South America"].remove("Brazil")
    continent_hierarchy1["Oceania"]["Melanesia"].append("Brazil")
    continent_hierarchy2 = copy.deepcopy(continent_hierarchy1)
    continent_hierarchy2["Europe"]["Northern Europe"].remove("United Kingdom")
    continent_hierarchy2["Africa"]["Northern Africa"].append("United Kingdom")
    continent_hierarchy2["Europe"]["Eastern Europe"].remove("Romania")
    continent_hierarchy2["Americas"]["Northern America"].append("Romania")
    continent_hierarchy3 = copy.deepcopy(continent_hierarchy2)
    continent_hierarchy3["Africa"]["Northern Africa"].remove("United Kingdom")
    continent_hierarchy3["Africa"]["Southern Africa"].append("United Kingdom")
    continent_hierarchy4 = copy.deepcopy(continent_hierarchy2)
    continent_hierarchy5 = copy.deepcopy(continent_hierarchy1)
    continent_hierarchy6 = copy.deepcopy(continent_hierarchy)

    df = pandas.read_excel('population-and-demography-modified.xlsx', skiprows=0)

    years = list(set(df['Year'].tolist()))
    years.sort()

    # create object
    data = []

    for y in years:
        data.append({'time': y, 'children': []})
        
        if int(y) < 1958:
            continent_hierarchy_now = continent_hierarchy
        elif int(y) < 1965:
            continent_hierarchy_now = continent_hierarchy1
        elif int(y) < 1970:
            continent_hierarchy_now = continent_hierarchy2
        elif int(y) < 1980:
            continent_hierarchy_now = continent_hierarchy3
        elif int(y) < 1990:
            continent_hierarchy_now = continent_hierarchy4 
        elif int(y) < 2000:
            continent_hierarchy_now = continent_hierarchy5
        else: 
            continent_hierarchy_now = continent_hierarchy6

        for continent_name in continent_hierarchy_now:
            

            data[-1]['children'].append({'name' : continent_name, 'children' : []})

            for region_name in continent_hierarchy_now[continent_name]:
                
                data[-1]['children'][-1]['children'].append({'name' : region_name, 'children' : []})

                for country_name in continent_hierarchy_now[continent_name][region_name]:
                    # print(y, continent_name, region_name, country_name)
                    tmp = df.loc[(df['Country name'] == country_name) & (df['Year'] == y)]['Population'].tolist()
                    if len(tmp) > 0:
                        data[-1]['children'][-1]['children'][-1]['children'].append({'name': country_name, 'value': tmp[0]})
                   

    return data 

def parse_and_write(client):
    name = "world-population-scramble"
    display_name = "Population data modified"
    desc = "This contains the population of every country from 1950 to 2021. The countries are grouped in continents and subregions. Some random changes are done to thestructure."

    db = client['TreeMap']
    index = db["TreeDataIndex"]
    data = db['TreeData']

    
    if index.count_documents({'name' : name}, limit = 1) == 0:
      dta = parse_population_data_2()
      index.insert_one({'name' : name, 'display_name' : display_name, 'description' : desc})
      data.insert_one({'name' : name, 'data' : dta})
      print("Dataset %s added in the DB"%(name))
    else:
      print("Dataset %s already in the DB. Skipping..."%(name))



if __name__ == '__main__':
    data = parse_population_data_2()