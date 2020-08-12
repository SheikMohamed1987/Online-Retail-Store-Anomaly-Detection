#Import Required Packages

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from statsmodels.distributions.empirical_distribution import ECDF

#Data Ingestion
@st.cache(allow_output_mutation=True)
def load_data():
    online_retail_data = pd.read_excel('Online Retail.xlsx', sheet_name='Online Retail')
    return online_retail_data

online_retail_data = load_data()
#Let's create new column 'Revenue' in sterling => qty*unit Price
online_retail_data['Revenue'] = online_retail_data['Quantity']*online_retail_data['UnitPrice']

#Remove Null records before further analysis.
online_retail_data.dropna(inplace=True)

# Remove duplicate items
online_retail_data.drop_duplicates(inplace=True)

#let's change data type for cust ID as int
online_retail_data['CustomerID'] = online_retail_data['CustomerID'].astype(int)

# Check and remove transactions with cancelled items.
online_retail_data = online_retail_data[~online_retail_data.InvoiceNo.str.contains('C', na=False)]

online_retail_data_UK = online_retail_data[online_retail_data['Country']=='United Kingdom']

# Lets create a purchase date column for date values only
online_retail_data_UK['Purchase_Date'] = online_retail_data_UK.InvoiceDate.dt.date

#Compute time between purchases for each customer
#Let's have a df that groups dataset by cust ID and Purchase dateS
online_retail_data_UK_grp_by_custID_PD = online_retail_data_UK.groupby(['CustomerID','Purchase_Date']).size().reset_index()

#Let's rename as Item count
online_retail_data_UK_grp_by_custID_PD.rename(columns={0: 'Item_Count'},inplace=True)


#Compute time lag between purchase for each customer
online_retail_data_UK_grp_by_custID_PD['Purchase_Date_lagged'] = (online_retail_data_UK_grp_by_custID_PD.sort_values(by=['Purchase_Date'], ascending=True)
                       .groupby(['CustomerID'])['Purchase_Date'].shift(1))

#let's change data type for Purchase_Date and Purchase_Date_lagged
online_retail_data_UK_grp_by_custID_PD['Purchase_Date'] = pd.to_datetime(online_retail_data_UK_grp_by_custID_PD['Purchase_Date'])
online_retail_data_UK_grp_by_custID_PD['Purchase_Date_lagged'] = pd.to_datetime(online_retail_data_UK_grp_by_custID_PD['Purchase_Date_lagged'])


# Compute the purchase pattern - between purchase days
online_retail_data_UK_grp_by_custID_PD['Between_purchase_days'] = online_retail_data_UK_grp_by_custID_PD.apply(lambda x: (x.Purchase_Date - x.Purchase_Date_lagged), axis=1)

#change dtype
online_retail_data_UK_grp_by_custID_PD['Between_purchase_days'] = online_retail_data_UK_grp_by_custID_PD['Between_purchase_days'].astype('timedelta64[D]')

#Let's filter the customers who has 20 or more purchases during entire year.
#Business may be interested and need to look at those most frequent customers risk to churn
online_retail_data_UK_Final= online_retail_data_UK_grp_by_custID_PD.groupby('CustomerID').filter(lambda g: g.Purchase_Date.count() > 20)


#let's write a fn that calculates 90th percentile between purchase days (BPD) for each customer and store in seperate column
@st.cache
def Calculate_BPD(custID):
    ecdf = ECDF(online_retail_data_UK_Final[online_retail_data_UK_Final['CustomerID']==custID]['Between_purchase_days'].dropna())
    BPD_Days = np.percentile(ecdf.x,90)
    return BPD_Days

# Compute the BPD 90th percentile
online_retail_data_UK_Final['BPD_90_Percent'] = online_retail_data_UK_Final.apply(lambda x: (Calculate_BPD(x.CustomerID)), axis=1)

online_retail_data_UK_Final['BPD_90_Percent'] = online_retail_data_UK_Final['BPD_90_Percent'].astype('timedelta64[D]')


# write a fn that takes customer ID and returns if at risk to churn
churnrisk=''
@st.cache
def Calculate_risk_forChurn(custID):
    Current_Date = online_retail_data_UK_Final['Purchase_Date'].max()
    CustID_Last_Purchase = online_retail_data_UK_Final[online_retail_data_UK_Final['CustomerID'] == custID]['Purchase_Date'].max()
    CustID_Last_Purchase_from_CurrentDate = Current_Date - CustID_Last_Purchase

    BPD_90_percent = online_retail_data_UK_Final[online_retail_data_UK_Final['CustomerID'] == custID]['BPD_90_Percent'].head(1)
    BPD_90_percent = BPD_90_percent.dt.days
    BPD_90_percent = pd.DataFrame(BPD_90_percent)
    BPD_90_percent = BPD_90_percent.BPD_90_Percent.values

    if (CustID_Last_Purchase_from_CurrentDate.days >= BPD_90_percent[0]):
        churnrisk = 'Customer is at risk to churn'
    else:
         churnrisk = 'Customer is not at risk to churn'
        # select customer id
    return churnrisk

df = online_retail_data_UK_Final['CustomerID'].unique()

Cust_ID = st.sidebar.selectbox("Choose Customer ID", df[28:38])

def visualize(Cust_ID):
    ecdf = ECDF(online_retail_data_UK_Final[online_retail_data_UK_Final['CustomerID'] == Cust_ID]['Between_purchase_days'].dropna())
    plt.plot(ecdf.x, ecdf.y)
    plt.title('Customer Between Purchase Days ECDF Plot')
    plt.xlabel('Between Purchase Days')
    plt.ylabel('Cumulative probability')
    plt.show()

st.title("Online Retail Store - Customer Churn Modeling - Anomaly Detection")
visualize(Cust_ID)
st.pyplot()

CustID_Last_Purchase = online_retail_data_UK_Final[online_retail_data_UK_Final['CustomerID'] == Cust_ID]['Purchase_Date'].max()
st.write('Customers last purchase date from current date in dataset [2011/12/09] - ' + str(CustID_Last_Purchase))

BPD_90_percent = online_retail_data_UK_Final[online_retail_data_UK_Final['CustomerID'] == Cust_ID][
    'BPD_90_Percent'].head(1)
BPD_90_percent = BPD_90_percent.dt.days
BPD_90_percent = pd.DataFrame(BPD_90_percent)
BPD_90_percent = BPD_90_percent.BPD_90_Percent.values
st.write('Customers Between Purchase Days 90th Percentile - ' + str(BPD_90_percent) + ' Days')
churnrisk = Calculate_risk_forChurn(Cust_ID)
st.write(churnrisk)