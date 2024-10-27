import requests
import xmltodict
import json


def get():
    r = requests.get('https://www.nbkr.kg/XML/daily.xml')
    data_dict = xmltodict.parse(r.content)
    print(data_dict)


    rates = [
         {
              'Nominal': i['Nominal'],
              'ISOCode': i['@ISOCode'],
              'Value': i['Value']
         }
        for i in data_dict['CurrencyRates']['Currency']
    ]

    if rates:
        try:
            with open("C:/Users/User/Desktop/projects/python/django/bank/main/json_files/exchange_rates.json", 'w', encoding='utf-8') as file:
                    json.dump(rates, file, ensure_ascii=False, indent=4)
                    
        except:
             print('error')

    
get()