
import streamlit as st
import pandas as pd


st.set_page_config(page_title="Supplier Profit Calculator", layout="wide")
st.title("Supplier Quality & Profitability Calculator")

st.sidebar.header("Production")
thickness=st.sidebar.number_input('Thickness mm',value=19.0)
width=st.sidebar.number_input('Input width mm',value=75.0)
saws=st.sidebar.number_input('Number of saws',value=2,step=1)
shifts=st.sidebar.number_input('Shifts',value=2,step=1)
hours=st.sidebar.number_input('Hours per shift/month',value=160)

st.sidebar.header('Labour')
ops=st.sidebar.number_input('Operators',value=3)
op_sal=st.sidebar.number_input('Operator salary',value=1800)
fd=st.sidebar.number_input('Forklift drivers',value=1)
fd_sal=st.sidebar.number_input('Forklift salary',value=1500)
workers=st.sidebar.number_input('Workers',value=1)
worker_sal=st.sidebar.number_input('Worker salary',value=1500)

st.sidebar.header('Monthly machine costs')
elec=st.sidebar.number_input('Electricity',value=0)
maint=st.sidebar.number_input('Maintenance',value=0)
blades=st.sidebar.number_input('Blades',value=0)
over=st.sidebar.number_input('Other overhead',value=0)

qualities=['Q1','Q1 Short','Q2','Q3','Q4','Q5','Waste']
width_factor={'Q1':75,'Q1 Short':75,'Q2':75,'Q3':61,'Q4':50,'Q5':75,'Waste':0}

st.header('Selling Prices €/m³')
prices={q:st.number_input(f'{q} price',value=float(v)) for q,v in {'Q1':650,'Q1 Short':500,'Q2':400,'Q3':250,'Q4':120,'Q5':700,'Waste':0}.items()}

cols=st.columns(2)

def supplier(col,name,defaults):
    with col:
        st.subheader(name)
        purchase=st.number_input(f'{name} purchase €/m³',value=defaults['purchase'])
        speed=st.number_input(f'{name} speed m/min',value=defaults['speed'])
        vals={}
        for q,d in defaults['q'].items():
            vals[q]=st.number_input(f'{name} {q} %',value=d)
    return purchase,speed,vals

A=supplier(cols[0],'Supplier A',{'purchase':235.0,'speed':38.5,'q':{'Q1':66.0,'Q1 Short':8.0,'Q2':10.0,'Q3':6.0,'Q4':4.0,'Q5':3.0,'Waste':3.0}})
B=supplier(cols[1],'Supplier B',{'purchase':235.0,'speed':34.0,'q':{'Q1':57.0,'Q1 Short':12.0,'Q2':12.0,'Q3':8.0,'Q4':5.0,'Q5':3.0,'Waste':3.0}})

prod_hours=hours*shifts
labor=((ops*op_sal)+(fd*fd_sal)+(workers*worker_sal))*shifts
labor_hr=labor/prod_hours
machine_hr=(elec+maint+blades+over)/prod_hours


def calc(data):
    purchase,speed,mix=data
    lmh=speed*saws*60
    input_m3h=(thickness/1000)*(width/1000)*lmh
    revenue_input=0
    recovered=0
    for q,pct in mix.items():
        share=pct/100
        factor=width_factor[q]/75
        sellable=share*factor
        revenue_input+=sellable*prices[q]
        recovered+=sellable
    revenue_hr=revenue_input*input_m3h
    material_hr=purchase*input_m3h
    profit_hr=revenue_hr-material_hr-labor_hr-machine_hr
    annual_profit=profit_hr*prod_hours*12
    return {'Revenue/h':round(revenue_hr,2),'Profit/h':round(profit_hr,2),'Annual Profit':round(annual_profit,2),'Recovered %':round(recovered*100,2),'Input m3/h':round(input_m3h,3),'Purchase':purchase,'Q1':mix['Q1']}

ra=calc(A)
rb=calc(B)

df=pd.DataFrame({'Supplier A':ra,'Supplier B':rb})
st.dataframe(df)

breakeven=ra['Purchase']*(B[2]['Q1']/A[2]['Q1'])
discount=B[0]-breakeven
st.metric('Supplier B break-even price',f'€{breakeven:.2f}')
st.metric('Required discount',f'€{discount:.2f}')

chart=pd.DataFrame({'Supplier':['A','B'],'Profit/h':[ra['Profit/h'],rb['Profit/h']]})
st.plotly_chart(px.bar(chart,x='Supplier',y='Profit/h',title='Profit per Hour'),use_container_width=True)

st.subheader('Sensitivity Analysis')
rows=[]
for p in range(160,261,10):
    rows.append({'Supplier B Price':p,'Difference to Break-even':round(p-breakeven,2)})
st.dataframe(pd.DataFrame(rows))
