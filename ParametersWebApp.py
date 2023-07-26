# ========== (c) JP Hwang 2/9/20  ==========

import logging

# ===== START LOGGER =====
logger = logging.getLogger(__name__)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
root_logger.addHandler(sh)

import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np


import streamlit as st
from io import StringIO 


st.title("DESCRIPTION AND AIM OF THIS WEBAPP")
st.markdown('**The aim of this app is to graphs trend of every features**')
st.markdown( '- **In the section I)** TOBs parameters are listed')
st.markdown( '- **In the section II)** a general description of every features is given')
st.markdown( '- **In the section III)** is shown as create graphs of every features')
st.markdown( '- **In the section IV)** correlation and heatmap among features is analyzed ')
st.markdown( '- **In the section V)** a possible previsional model for unknown parameters is given')
#upload single file and display it as a dataframe
st.title("I) Table of all TOBs")
Data = pd.read_excel("ParametriLaserBertaldi.xlsx")
Data


#CODICE NON VISUALIZZATO
#IL FILE CHE CARICO SI CHIAMA DATA SUL QUALE FACCIO UN PO' DI MODIFICHE.
#POI LO RINOMINO IN PARAMETER PER POTERCI GIOCARE
Data.drop_duplicates(keep='first', ignore_index=True, inplace=True)
Data.insert(loc=2, column='Mat_Description', value=Data.Materiale)
Data['Mat_Description']=Data['Mat_Description'].map({'AlMg3':'Alluminio','CuZn37: Rame-ZN':'Alluminio',\
'Cu-OF':'Rame','S420MC':'Fe_5-25mm','X5CrNi18-10':'INOX','DC01+ZE25/25-APC':'Acciaio-ZN','DC01':'Fe_1-5mm'\
,'X5CrNi18-10_Foil':'INOX_foil', 'DX51D+Z275-N-A-C':'Zinc coated steel'})

Data.insert(loc=2, column="Material_code", value=Data["Materiale"])

Data.Material_code=Data.Material_code.map({'AlMg3':1,'CuZn37':2,'Cu-OF':3,'S420MC':4,'X5CrNi18-10':5,'DC01+ZE25/25-APC':6,'DC01':7,
                            'X5CrNi18-10_Foil':8,'DX51D+Z275-N-A-C':9, 'Focal':11,'Startup':12, 'Startup2':13,'VPO':14 })
Data.drop(['Note', 'Coll.Pie','SO Cut2', 'SO Cut3', 'Power2','Power3', 'Speed2', 'Speed3', 'Focal2', 'Focal3',
      'Pressure2', 'Pressure3'], axis=1, inplace=True)
conditions = [(Data['Coll.Cut'] == 'F120'),(Data['Coll.Cut'] == 'F100'),(Data['Coll.Cut'] == 'F85'),
(Data['Coll.Cut'] == 'F70'),(Data['Coll.Cut'] == 'F55')]
values = [2.19, 2.75,3.14,4.63,7.5]
Data["RayleighLenght"] = np.select(conditions, values)
Data['Coll.Cut']=Data['Coll.Cut'].map({'F120':120, 'F100':100,'F85':85,'F70':70,'F55':55})
Data.rename(columns ={'Materiale':'Material','Spessore':'Thickness[mm]','SO Cut1':'StandOff[mm]', 'Power1':'LaserPower[W]','Speed1':'Speed[mm/min]','Focal1':'Focal[mm]','Pressure1':'Pressure[Bar]','Coll.Cut':'Collimator[mm]'}, inplace = True)
#Insertion BEAM DIAMETER 86%
Data["SpotDiam[um]"] = 100*190.5/Data['Collimator[mm]']#FiberCorexCuttingLensEFL
Data["SpotDiam[um]"]=Data["SpotDiam[um]"]
#Insertion BEAM DIAMETER 86% al TOP e BOTTOM del pezzo di taglio 
Data["BeamTop[um]"]=2*((Data["SpotDiam[um]"]/2)*(1+(Data["Focal[mm]"]/Data["RayleighLenght"])**(2))**(0.5))
Data["BeamBottom[um]"]=2*((Data["SpotDiam[um]"]/2)*(1+((Data["Thickness[mm]"]+Data["Focal[mm]"])/Data["RayleighLenght"])**(2))**(0.5))
Data["BeamMedium[um]"]=2*((Data["SpotDiam[um]"]/2)*(1+(((Data["Thickness[mm]"]/2)+Data["Focal[mm]"])/Data["RayleighLenght"])**(2))**(0.5))
Data["BeamAverage[um]"]=(Data["BeamTop[um]"]+Data["BeamBottom[um]"]+Data["BeamMedium[um]"])/3
#Insertion POWER DENSITY
Data["PowerDensityTop[W/cm2]"]=(Data["LaserPower[W]"]/ (3.14*(Data["BeamTop[um]"]/20000)**2))
Data["PowerDensityBottom[W/cm2]"]=(Data["LaserPower[W]"]/ (3.14*(Data["BeamBottom[um]"]/20000)**2))
Data["PowerDensityAverage[W/cm2]"]=(Data["LaserPower[W]"]/ (3.14*(Data["BeamAverage[um]"]/20000)**2))
#Insertion ENERGY ABSORBED
#Time on material ts=Spot Diameter/Speed
#Energy released=Laser power*ts*absorption
Data["Speed[mm/s]"]=(Data["Speed[mm/min]"]/60).round(2)
Data["EnergySurface[J/mm2]"]=(0.01*0.001*Data["BeamAverage[um]"]/(Data["Speed[mm/s]"])*Data['PowerDensityAverage[W/cm2]'])
Data["EnergyDensity[J/mm3]"]=(Data["EnergySurface[J/mm2]"]/Data["Thickness[mm]"])
#Data.drop(["Speed[mm/min]"], axis=1, inplace=True)
Data=Data.drop_duplicates(keep='first',ignore_index=False)

Data.insert(loc=2, column='LaserPower', value=Data['LaserPower[W]'])
Data['LaserPower']=Data['LaserPower'].map({10000:'10 kW',3000: '3 kW', 4000:'4 kW', 6000:'6 kW', 4400:'4,4 kW', 5000:'5 kW', 4200:'4.2 kW', 5200:'5,2 kW',
1000:'1 kW', 1100:'1.1 kW', 1200:'1.2 kW', 1900:'1.9 kW', 500:'0.5 kW', 1300:'1.3 kW', 4500:'4.5 kW', 500:'0.5 kW', 5500:'5.5 kW', 500:'0.5 kW', 800:'0.8 kW', 8000:'8 kW',3800:'3.8 kW', 12000 :'1,2 kW',
                                                  12000:'12 kW',    3900:'3.9 kW', 15000:'15 kW', 2000:'2 kW'})
Data.insert(loc=3, column='Collimator', value=Data['Collimator[mm]'])
Data['Collimator']=Data['Collimator'].map({120:'120mm',85: '85mm', 100:'100mm', 55:'55mm', 70:'70mm'})




Data=Data.drop(['Speed[mm/s]','StandOff[mm]','RayleighLenght', 'SpotDiam[um]',
       'BeamTop[um]', 'BeamBottom[um]', 'BeamMedium[um]', 'BeamAverage[um]',
       'PowerDensityTop[W/cm2]', 'PowerDensityBottom[W/cm2]',
       'PowerDensityAverage[W/cm2]','EnergyDensity[J/mm3]'], axis=1)
Data=Data[(Data.Tabella=='YLS2000HY')|(Data.Tabella=='YLS4000HY')|(Data.Tabella=='YLS6000HY')|(Data.Tabella=='YLS8000HY')|(Data.Tabella=='YLS10000HY')|(Data.Tabella=='YLS12000HY')|(Data.Tabella=='YLS15000HY')]
Data_Mat={'Material': Data.Material.unique()}


MaterialList=pd.DataFrame(data=Data_Mat)
MaterialList.insert(loc=1, column='Material code', value=MaterialList.Material)
MaterialList.insert(loc=2, column='Material description', value=MaterialList.Material)

MaterialList['Material description']=MaterialList['Material description'].map({'AlMg3':'Alluminio','CuZn37': 'Rame-ZN',\
'Cu-OF':'Rame','S420MC':'Fe_5-25mm','X5CrNi18-10':'INOX','DC01+ZE25/25-APC':'Acciaio-ZN','DC01':'Fe_1-5mm'\
,'X5CrNi18-10_Foil':'INOX_foil', 'DX51D+Z275-N-A-C':'Zinc coated steel', 'Focal':'Focal','Startup':'Startup', 'Startup2':'Startup2','VPO':'VPO'})

MaterialList['Material code']=MaterialList['Material code'].map({'AlMg3':1,'CuZn37':2,'Cu-OF':3,'S420MC':4,'X5CrNi18-10':5,'DC01+ZE25/25-APC':6,'DC01':7,
                            'X5CrNi18-10_Foil':8,'DX51D+Z275-N-A-C':9, 'Focal':11,'Startup':12, 'Startup2':13,'VPO':14 })
MaterialList=MaterialList.sort_values(by='Material code')
MaterialList=MaterialList.set_index('Material')


Data.insert(loc=9, column='Nozzle_Code', value=Data.Nozzle)
Data['Nozzle_Code']=Data['Nozzle_Code'].map({'ST 1.5':'1', 'ST 2.0':'2', 'ST 2.5':'3', 'RT 6.0':'4', 'ST 3.0':'5', 'RT 10.0':'6',
       'SMT 3.5':'7', 'SMT 5.0':'8', 'DT 1.5':'9', 'DT 1.75':'10', 'DT 2.5':'11', 'SMT 4.0':'12',
       'DT 2':'13', 'RT 4.0':'14', 'VPO 2.0':'15', 'DL 3.0':'16', 'DT 1.25':'17', 'SMT 3.0':'18'})

Data.Nozzle_Code=Data.Nozzle_Code.astype('int64')

Data_Nozzle={'Nozzle': Data.Nozzle.unique()}
NozzleList=pd.DataFrame(data=Data_Nozzle)
NozzleList.insert(loc=1, column='NozzleCode', value=NozzleList.Nozzle)

NozzleList['NozzleCode']=NozzleList['NozzleCode'].map({'ST 1.5':1, 'ST 2.0':2, 'ST 2.5':3, 'RT 6.0':4, 'ST 3.0':5, 'RT 10.0':6,
       'SMT 3.5':7, 'SMT 5.0':8, 'DT 1.5':9, 'DT 1.75':10, 'DT 2.5':11, 'SMT 4.0':12,
       'DT 2':13, 'RT 4.0':14, 'VPO 2.0':15, 'DL 3.0':16, 'DT 1.25':17, 'SMT 3.0':18})

NozzleList=NozzleList.sort_values(by='NozzleCode')
NozzleList.NozzleCode=NozzleList.NozzleCode.astype('int64')
NozzleList=NozzleList.set_index('NozzleCode')

#INIZIO CODICE VISUALIZZATO

# PARAGRAPH 1: Header
st.subheader("TOBs cleaned with only fundamental features")
st.write(Data)
st.title("II) General info of every features")
DF=Data.copy()


DF['LaserPower[W]']= DF['LaserPower[W]'].astype('object')


DF=DF.drop(['Tabella', 'Material', 'Material_code', 'Nozzle', 'Mat_Description'], axis=1)
def get_inform(DF):
    check_df = pd.DataFrame()
    check_df['Tot Values'] = DF.count()
    check_df['Max'] = DF.max()
    check_df['Min'] = DF.min()
    check_df['Different values'] = DF.nunique() 
    return check_df
get_inform(DF)
st.write(get_inform(DF))




# CORRELATION AND SCATTERPLOT ON RANGED AND SINGLE PARAMETERS


st.title("III) Scatterplot with multiselection")
st.subheader("Machine parameters can be selected in two modes: RANGE (in the range parameters) and/or SINGLE (in the cathegorical parameters)")
st.header('Selection of axis')

#st.write(Data)
corr_x3 = st.selectbox("**SELECT X AXIS**", options=Data.columns, index=Data.columns.get_loc("Thickness[mm]"))
corr_y3 = st.selectbox("**SELECT Y AXIS**", options=Data.columns, index=Data.columns.get_loc("Speed[mm/min]"))




#st.title("Ranged parameters")

st.subheader('SELECTION OF RANGE PARAMETERS')
st.info('To switch off this section put min and max limits at 0!!', icon="ℹ️")
Thickness= st.selectbox("**SELECT RANGE OF THICKNESS**",options=Data.columns, index=Data.columns.get_loc("Thickness[mm]"))
min_Thickness = st.number_input("Min Thickness[mm]", value=0, min_value=0)
max_Thickness = st.number_input("Max Thickness[mm]", value=30, min_value=0)

LaserPower= st.selectbox("**SELECT RANGE OF Laser Power**",options=Data.columns, index=Data.columns.get_loc("LaserPower[W]"))
min_LaserPower = st.number_input("Min LaserPower[W]", value=10000, min_value=0)
max_LaserPower = st.number_input("Max LaserPower[W]", value=10000, min_value=0)


Speed= st.selectbox("**SELECT RANGE OF SPEED**", options=Data.columns, index=Data.columns.get_loc("Speed[mm/min]"))
min_Speed = st.number_input("Min Speed [mm/min]", value=160, min_value=0)
max_Speed = st.number_input("Max Speed [mm/min]", value=90000, min_value=0)
#SpeedValue= st.number_input("Speed", value=10, min_value=0)


Pressure= st.selectbox("**SELECT RANGE OF PRESSURE**", options=Data.columns, index=Data.columns.get_loc("Pressure[Bar]"))
min_Pressure = st.number_input("Min Pressure", value=0, min_value=0)
max_Pressure = st.number_input("Max Pressure", value=17, min_value=0)


MatCode= st.selectbox("**SELECT RANGE OF MATERIAL CODE**", options=Data.columns, index=Data.columns.get_loc("Material_code"))
min_MatCode = st.number_input("Min Material code", value=5, min_value=0)
max_MatCode = st.number_input("Max Material code", value=6, min_value=0)

NozzleCode= st.selectbox("**SELECT RANGE OF NOZZLE CODE**", options=Data.columns, index=Data.columns.get_loc('Nozzle_Code'))
min_NozzleCode = st.number_input("Min Nozzle code", value=0, min_value=0)
max_NozzleCode = st.number_input("Max Nozzle code", value=9, min_value=0)

#st.title("Cathegorical parameters")
st.subheader('SELECTION OF CATHEGORICAL PARAMETERS')
st.info('To filter only on cathegorical parameters put previous *range parameters* at 0!!', icon="ℹ️")
F8= st.selectbox("**LASER POWER**", options=Data['LaserPower[W]'].unique(), index=Data.columns.get_loc("LaserPower[W]"))
F9= st.selectbox("**MATERIAL**", options=Data['Material'].unique(), index=Data.columns.get_loc("Material"))
F11= st.selectbox("**THICKNESS[mm]**", options=Data['Thickness[mm]'].unique(), index=Data.columns.get_loc('Thickness[mm]'))

Nozzle= st.selectbox("**Nozzle**", options=Data['Nozzle'].unique(), index=Data.columns.get_loc('Nozzle'))




#FGas= st.selectbox("**Gas**", options=df2['Gas'].unique(), index=df2.columns.get_loc('Gas'))


corr_col3 = st.radio("**SELECT COLOR VARIABLE**", options=['Material','Nozzle','Pressure[Bar]', 'LaserPower','Gas', 'Focal[mm]'], index=1)

tmp_df3 = Data[(Data['LaserPower[W]']==F8)|((Data['LaserPower[W]'] >= min_LaserPower)&(Data['LaserPower[W]'] <= max_LaserPower))]                      [(Data['Nozzle']==Nozzle)|((Data['Nozzle_Code'] >= min_NozzleCode)&(Data['Nozzle_Code'] <= max_NozzleCode))]        [(Data[Thickness] == F11)|((Data[Thickness] >= min_Thickness)&(Data[Thickness] <= max_Thickness))][(Data[Pressure] >= min_Pressure)&(Data[Pressure] <= max_Pressure)&(Data[Speed] >= min_Speed)&(Data[Speed] <= max_Speed)]    [(Data['Material']==F9)|((Data[MatCode] >= min_MatCode)&(Data[MatCode] <= max_MatCode))]


fig = px.scatter(tmp_df3, x=corr_x3, y=corr_y3, template="plotly_white", render_mode='webgl',
                 color=corr_col3, hover_data=['Nozzle','Pressure[Bar]', 'LaserPower', 'Material_code', 'Gas', 'Focal[mm]', 'Material'], color_continuous_scale=px.colors.sequential.OrRd,
                 title='')
fig.update_traces(mode="markers", marker={"line": {"width": 0.4, "color": "slategrey"}})
st.header("--> Scatterplot of filtered parameters")
st.write(fig)

#df3 = pd.read_csv("df3.csv", index_col=0).reset_index(drop=True)

st.subheader("Materials and Nozzle list")
st.write(MaterialList)
st.write(NozzleList)





# correlation heatmap
Data_reduced=Data[['LaserPower[W]','Thickness[mm]','Speed[mm/min]','Pressure[Bar]','EnergySurface[J/mm2]', 'Focal[mm]']]

st.title ("IV) Correlation and heatmap")
st.subheader('Select parameter to include on heatmap')
hmap_params = st.multiselect("Features", options=list(Data_reduced.columns), default=[p for p in Data_reduced.columns if "fg" in p])
hmap_fig = px.imshow(Data_reduced[hmap_params].corr(), color_continuous_scale=('yellow', 'red'), facet_col_spacing=0.99, facet_row_spacing=0.5, title='CORRELATIONE AMONG LASER PARAMETERS')
st.write(hmap_fig)



#PARAGRAPH: ESTIMATION OF NEW PARAMETERS
EstimatedParameters= pd.read_excel('Estimated parameters_ok.xlsx')
st.title("V) Previsional model for unknown parameters")
EstimatedParameters = EstimatedParameters.reset_index(drop=True)
corr_xEP = st.selectbox("Correlation - X variable", options=EstimatedParameters.columns, index=EstimatedParameters.columns.get_loc("Thickness[mm]"))
corr_yEP = st.selectbox("Correlation - Y variable", options=EstimatedParameters.columns, index=EstimatedParameters.columns.get_loc("SpeedTH[mm/min]"))
corr_colEP = st.radio("Correlation - color variable", options=["Gas",'LaserPower[W]'], index=1)
#corr_filtEP= st.selectbox("Filter variable", options=EstimatedParameters.columns, index=EstimatedParameters.columns.get_loc("LaserPower[W]"))
#min_filtEP = st.number_input("Minimum value", value=8000, min_value=0)
#max_filtEP = st.number_input("Maximum value", value=10000, min_value=0)

#MaterialCode= st.selectbox("**SELECT RANGE OF MATERIAL CODE**", options=EstimatedParameters.columns, index=EstimatedParameters.columns.get_loc("MaterialCode"))
#min_MaterialCode = st.number_input("Min MaterialCode", value=4, min_value=0)
#max_MaterialCode = st.number_input("Max MaterialCode", value=6, min_value=0)

F18= st.selectbox("**LASER POWER**", options=EstimatedParameters['LaserPower[W]'].unique(), index=EstimatedParameters.columns.get_loc("LaserPower[W]"))
F19= st.selectbox("**MATERIAL**", options=EstimatedParameters['Material'].unique(), index=EstimatedParameters.columns.get_loc("Material"))




#tmp_dfEP = EstimatedParameters[(EstimatedParameters['LaserPower[W]']==F18)|(EstimatedParameters[corr_filtEP] > min_filtEP)&(EstimatedParameters[corr_filtEP] <= max_filtEP)][(EstimatedParameters['Material']==F9)|((EstimatedParameters[MaterialCode] >= min_MaterialCode)&(EstimatedParameters[MaterialCode] <= max_MaterialCode))]
tmp_dfEP = EstimatedParameters[(EstimatedParameters['LaserPower[W]']==F18)|(EstimatedParameters['Material']==F9)]





fig = px.scatter(tmp_dfEP, x=corr_xEP, y=corr_yEP, template="plotly_white", render_mode='webgl',
                 color=corr_colEP, hover_data=['LaserPower[W]','Gas'], color_continuous_scale=px.colors.sequential.OrRd,
                 )
fig.update_traces(mode="markers", marker={"line": {"width": 0.4, "color": "slategrey"}})
st.subheader("ESTIMATED PARAMETERS")
st.write(fig)
st.write(tmp_dfEP)



































