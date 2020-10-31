import pandas as pd
import numpy as np
import requests
import json
import copy
import io



def get_data(country, code):

    if country == 'brazil':
        
        return brazil(code)


    elif country == 'unitedstates':

        return unitedstates(code)


    elif (country in euro19_reference.keys()) or (country in euro27_reference.keys()):

        return eu(code)


    elif country in ['eurozone','europeanunion']:

        return eu(code)

    else:

        print('Country Not Found.')




def brazil(code):

    url = f'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json'
    f = requests.get(url)
    ipdata = f.json()
    df = pd.DataFrame(ipdata)
    df['data'] = pd.to_datetime(df['data'],format='%d/%m/%Y')
    df['data'] = df['data'].dt.date
    df.index = df['data']
    df = df.drop(columns = 'data')
    df.valor = df.valor.replace('','NaN')
    df.valor = df.valor.astype(float)

    df = df.dropna()

    df.columns = ['value']
    
    return df

def unitedstates(code):

        url = f'https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key=c08cb5f03357dfc29fe76908708b7be0&file_type=json'
        f = requests.get(url)
        ipdata = f.json()
        df = pd.DataFrame(list(ipdata['observations']))
        df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d')
        df['date'] = df['date'].dt.date
        df.index = df['date']
        df = df.drop(columns = 'date')
        df.value = df.value[12:]
            
        df['value'] = df['value'].replace('.','NaN').dropna()
            

        df = df.drop(columns = ['realtime_end','realtime_start'])
        df.value = df.value.astype(float)

        df = df.dropna()
        
        df.columns = ['value']

        return df


def eu(code):

    code = f'{code[:3]}/{code[4:]}'
    url = f'https://sdw-wsrest.ecb.europa.eu/service/data/{code}'
    f = requests.get(url, headers={'Accept': 'text/csv'}).text
    df = pd.read_csv(io.StringIO(f))
    df = df.filter(['TIME_PERIOD','OBS_VALUE'])
    df.columns = ['date','value']
    if type(df.iloc[0,0]) == np.int64:
        print(True)
        df.date = df.date.astype(str) + '-01-01'

    df.date = pd.to_datetime(df.date).dt.date
        
    df = df.set_index('date',drop = True)
    df.value = df.value.astype(float)

    df = df.dropna()

    return df




timeseries1 = {

    'brazil':{
        'gdp': {'code':1207, 'description':'GDP at current prices in R$','unit':'R$','freq':'A'},
        'gdppercapita': {'code':21775, 'description':'GDP per capita at current prices in R$','unit':'R$','freq':'A'},
        'mb': {'code':1788, 'description':'Monetary base - Monetary base (end-of-period balance)','unit':'c.m.u. (thousand)','freq':'M'},
        'm1': {'code':27841, 'description':'Money supply - M1 (end-of-period balance)','unit':'c.m.u. (thousand)','freq':'M'},
        'm2': {'code':27842, 'description':'Broad money supply - M2 (end-of-period balance)','unit':'c.m.u. (thousand)','freq':'M'},
        'm3': {'code':27813, 'description':'Broad money supply - M3 (end-of-period balance)','unit':'c.m.u. (thousand)','freq':'M'},
        'publicdebt': {'code':2053, 'description':'Net public debt - Balances in c.m.u. (million) - Total - Federal Government and Banco Central','unit':'c.m.u. (million)','freq':'M'},
    },

    'eurozone':{
        'gdp': {'code':'MNA.Q.N.I8.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.V.N', 'description':'Gross domestic product at market prices','unit':'Millions','freq':'Q'},
        'mb': {'code':'ILM.M.U2.C.LT00001.Z5.EUR', 'description':'Base money','unit':'Millions of Euro','freq':'M'},
        'm1': {'code':'BSI.M.U2.Y.V.M10.X.1.U2.2300.Z01.E', 'description':'Monetary aggregate M1','unit':'Millions of Euro','freq':'M'},
        'm2': {'code':'BSI.M.U2.Y.V.M20.X.1.U2.2300.Z01.E', 'description':'Monetary aggregate M2','unit':'Millions of Euro','freq':'M'},
        'm3': {'code':'BSI.M.U2.Y.V.M30.X.1.U2.2300.Z01.E', 'description':'Monetary aggregate M3','unit':'Millions of Euro','freq':'M'},
        'publicdebt': {'code':'GFS.Q.N.I8.W0.S13.S1.C.L.LE.GD.T._Z.XDC._T.F.V.N._T', 'description':'Government debt (consolidated)','unit':'Millions of Euro','freq':'M'},
    },

    'europeanunion':{
        'gdp': {'code':'MNA.Q.N.B6.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.V.N', 'description':'Gross domestic product at market prices','unit':'Millions','freq':'Q'},
        'publicdebt': {'code':'GFS.Q.N.B6.W0.S13.S1.C.L.LE.GD.T._Z.XDC._T.F.V.N._T', 'description':'Government debt (consolidated)','unit':'Millions of Euro','freq':'M'},
    },


    'unitedstates': {
        'cbbalancesheet': {'code':'WALCL', 'description': 'Assets: Total Assets: Total Assets (Less Eliminations from Consolidation): Wednesday Level','unit':'Millions of Dollars','freq':'W'},
        'gdp': {'code':'GDP', 'description':'Gross Domestic Product','unit':'Billions of Dollars','freq':'Q'},
        'gdppercapita': {'code':'A939RX0Q048SBEA', 'description':'Real gross domestic product per capita','unit':'Dollars','freq':'Q'},
        'mb': {'code':'BOGMBASE', 'description':'Monetary Base; Total','unit':'Millions of Dollars','freq':'M'},
        'm1': {'code':'M1', 'description':'M1 Money Stock','unit':'Billions of Dollars','freq':'W'},
        'm2': {'code':'M2', 'description':'M2 Money Stock','unit':'Billions of Dollars','freq':'W'},
        'm3': {'code':'MABMM301USM189S', 'description':'M3 for the United States','unit':'National Currency','freq':'M'},
        'publicdebt': {'code':'GFDEBTN', 'description':'Federal Debt: Total Public Debt','unit':'Millions of Dollars','freq':'Q'},
    }
}

timeseries2 = {

    'brazil':{
        'exchangerate': {'code':1, 'description':'Exchange rate - Free - United States dollar (sale)','unit':'BRL','freq':'D'},
        'fundsrate': {'code':1178, 'description':'Interest rate - Selic in annual terms (basis 252)','freq':'D'},
        'inflation': {'code':433, 'description':'Broad National Consumer Price Index (IPCA)','freq':'M'},
        'population': {'code':21774, 'description':'Population','unit':'Thousands','freq':'A'},
        'popworkingage': {'code':24370, 'description':'Working age population - Continuos PNAD','unit':'Thousands','freq':'M'},
        'poplaborforce': {'code':24378, 'description':'Labor force population - Continuous PNAD','unit':'Thousands','freq':'M'},
        'popemployed': {'code':24379, 'description':'Employed population - Continuous PNAD','unit':'Thousands','freq':'M'},
        'popunemployed': {'code':24380, 'description':'Unemployed population - Continuous PNAD','unit':'Thousands','freq':'M'},
        'publicdebtgdp': {'code':4503, 'description':'Net public debt (% GDP) - Total - Federal Government and Banco Central','freq':'M'},
        'target_inflation': {'code':13521, 'description':'Target inflation rate','freq':'A'},
        'unemployment': {'code':24369, 'description':'Unemployment rate - PNADC','freq':'M'},
    },

    'eurozone':{
        'avggovyields': {'code':'GFS.M.N.I8.W0.S13.S1.N.L.LE.F3.T._Z.RT._T.F.V.A1._T', 'description':'Average nominal yields for total government debt securities','freq':'M'},
        'exchangerate': {'code':'EXR.D.USD.EUR.SP00.A', 'description':'US dollar/Euro','unit':'USD','freq':'D'},
        'govsurgdp': {'code':'GFS.Q.N.I8.W0.S13.S1._Z.B.B9._Z._Z._Z.XDC_R_B1GQ_CY._Z.S.V.CY._T', 'description':'Government deficit(-) or surplus(+) (as % of GDP)','freq':'Q'},
        'inflation': {'code':'ICP.M.U2.N.000000.4.ANR', 'description':'HICP - Overall index','freq':'M'},
        # 'population': {'code':'DD.A.I8.POPE.LEV.4D', 'description':'Population','unit':'Millions of Persons','freq':'A'},
        'popunemployed': {'code':'STS.A.I8.N.UNEH.LTT000.4.000', 'description':'Unemployment levels','unit':'Thousands','freq':'M'},
        'publicdebtgdp': {'code':'GFS.A.N.I8.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ._T.F.V.N._T', 'description':'Government debt (consolidated) (as % of GDP)','freq':'A'},
        'publicdebtgrowth': {'code':'GFS.Q.N.I8.W0.S13.S1.C.L.LE.GD.T._Z.XDC._T.F.V.GY._T', 'description':'Government debt (consolidated) (annual growth rate)','freq':'Q'},
        'unemployment': {'code':'STS.M.I8.S.UNEH.RTT000.4.000', 'description':'Unemployment rate','freq':'M'},
    },

    'europeanunion':{
        # 'avggovyields': {'code':'GFS.M.N.B6.W0.S13.S1.N.L.LE.F3.T._Z.RT._T.F.V.A1._T', 'description':'Average nominal yields for total government debt securities','freq':'M'},
        'govsurgdp': {'code':'GFS.Q.N.B6.W0.S13.S1._Z.B.B9._Z._Z._Z.XDC_R_B1GQ_CY._Z.S.V.CY._T', 'description':'Government deficit(-) or surplus(+) (as % of GDP)','freq':'Q'},
        # 'population': {'code':'DD.A.B6.POPE.LEV.4D', 'description':'Population','unit':'Millions of Persons','freq':'A'},
        'publicdebtgdp': {'code':'GFS.A.N.B6.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ._T.F.V.N._T', 'description':'Government debt (consolidated) (as % of GDP)','freq':'A'},
        'publicdebtgrowth': {'code':'GFS.Q.N.B6.W0.S13.S1.C.L.LE.GD.T._Z.XDC._T.F.V.GY._T', 'description':'Government debt (consolidated) (annual growth rate)','freq':'Q'},
        # 'unemployment': {'code':'STS.M.B6.S.UNEH.RTT000.4.000', 'description':'Unemployment rate','freq':'M'}, Não existe
    },

    'unitedstates': {
        'fundsrate': {'code':'FEDFUNDS', 'description':'Effective Federal Funds Rate','freq':'M'},
        'govsurgdp': {'code':'FYFSGDA188S', 'description':'Federal Surplus or Deficit [-] as Percent of Gross Domestic Product','freq':'A'},
        'inflation': {'code':'FPCPITOTLZGUSA', 'description':'Inflation, consumer prices for the United States','freq':'A'},
        'population': {'code':'POPTHM', 'description':'Population','unit':'Thousands','freq':'M'},
        'popworkingage': {'code':'LFWA64TTUSM647S', 'description':'Working Age Population: Aged 15-64: All Persons for the United States','unit':'Thousands','freq':'M'},
        'poplaborforce': {'code':'CLF16OV', 'description':'Civilian Labor Force Level','unit':'Thousands','freq':'M'},
        'popemployed': {'code':'CE16OV', 'description':'Employment Level','unit':'Thousands','freq':'M'},
        'popunemployed': {'code':'UNEMPLOY', 'description':'Unemployment Level','unit':'Thousands','freq':'M'},
        'publicdebtgdp': {'code':'GFDEGDQ188S', 'description':'Federal Debt: Total Public Debt as Percent of Gross Domestic Product','freq':'Q'},
        'unemployment': {'code':'UNRATE', 'description':'Unemployment Rate','freq':'M'},
    }
}


series1_reference = {
    'gdp': {
        'code':'MNA.A.N.XX.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.V.N',
        'description':'Gross domestic product at market prices',
        'unit': 'Millions of Euro',
        'freq':'A', 
        },
    'publicdebt': {
        'code':'GFS.Q.N.XX.W0.S13.S1.C.L.LE.GD.T._Z.XDC._T.F.V.N._T',
        'description':'Government debt (consolidated)',
        'unit': 'Millions of Euro', 
        'freq':'Q',
        },
}

series2_reference = {
    'govsurgdp': {
        'code':'EDP.A.N.XX.W0.S13.S1._Z.B.B9._Z._Z._Z.XDC_R_B1GQ._Z.S.V.N._T',
        'description':'Government deficit(-) or surplus(+) (Excessive deficit procedure, as % of GDP)',
        'freq':'A', 
        },
    'population': {
        'code':'ENA.A.N.XX.W0.S1.S1._Z.POP._Z._Z._Z.PS._Z.N',
        'description':'Total population',
        'unit': 'Thousands', 
        'freq':'A',
        }, 
    'popemployed': {
        'code':'STS.M.XX.N.UNEH.LTT000.4.000',
        'description':'Unemployment levels',
        'unit': 'Thousands', 
        'freq':'M',
        },
    'publicdebtgdp': {
        'code':'GFS.Q.N.XX.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T',
        'description':'Government debt (consolidated) (as % of GDP)',
        'freq':'Q',
        },
    'publicdebtgrowth': {
        'code':'GFS.Q.N.XX.W0.S13.S1.C.L.LE.GD.T._Z.XDC._T.F.V.GY._T',
        'description':'Government debt (consolidated) (annual growth rate)',
        'freq':'Q',
        },
    'unemployment': {
        'code':'STS.M.XX.S.UNEH.RTT000.4.000',
        'description':'Unemployment rate',
        'freq':'M',
        },
    
}



euro19_reference = {
    'austria':'AT',
    'belgium':'BE',
    'cyprus':'CY',
    'germany':'DE',
    'estonia':'EE',
    'spain':'ES',
    'finland':'FI',
    'france':'FR',
    'greece':'GR',
    'ireland':'IE',
    'italy':'IT',
    'lithuania':'LT',
    'luxembourg':'LU',
    'latvia':'LV',
    'malta':'MT',
    'netherlands':'NL',
    'portugal':'PT',
    'slovenia':'SI',
    'slovakia':'SK',
}

euro27_reference = {
    'sweden':'SE',
    'bulgaria':'BG',
    'czechrepublic':'CZ',
    'denmark':'DK',
    'croatia':'HR',
    'hungary':'HU',
    'poland':'PL',
    'romania':'RO'
}



forex = {
    
    'brazil': 1,
    'eurozone': 'EXR.D.USD.EUR.SP00.A',
    'europeanunion': 'EXR.D.USD.EUR.SP00.A',
    }


for euro_series, series_data in zip([series1_reference, series2_reference], [timeseries1, timeseries2]):
    
    for group in [euro19_reference,euro27_reference]:
        
        for country in group:
            
            data = copy.deepcopy(euro_series)
            
            for series in data:
                
                data[series]['code'] = data[series]['code'].replace('XX', group[country])
            
            series_data[country] = data
            
for group in [euro19_reference,euro27_reference]:

    for country in group:
        
        if country not in forex.keys():
        
            forex[country] = 'EXR.D.USD.EUR.SP00.A'