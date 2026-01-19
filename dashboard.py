import streamlit as st
import bls_manager as bls
import plotly.express as px


#Setting the page layout to wide and adding a title
st.set_page_config(layout="wide")
st.title("CPI Data Visualizer")

#initializing three columns for user inputs
col1, col2, col3 = st.columns(3)


cpi_manager = bls.BLS_data()

#Allows the user to select a date range for the CPI data
def slider():
    start_date, end_date = st.select_slider("Select Date Range", options=cpi_manager.available_dates(), value=(2024,2025))
    return start_date, end_date

#Plots CPI data with given parameters
def plot_cpi(start_date, end_date, region="South", item="All items"):
    data = cpi_manager.cpi_data_query(region, item, start_date, end_date)
    if data is None:
        st.error("Unable to fetch data due to API limitations. Please select an availible region and item.")
        return
    graph = px.line(data, x="date", y="value")
    st.plotly_chart(graph, width='stretch')  

#Allows the user to select a region for CPI data
def region_selection():
    area = st.selectbox("Select Region", options=cpi_manager.area_codes()["area_name"].tolist())
    return area

#Allows the user to select an item for CPI data
def item_selection():
    item = st.selectbox("Select Item", options=cpi_manager.item_codes()["item_name"].tolist())
    return item

#Displays a table of locally available CPI series
def availible_series():
    st.subheader("Locally Available CPI Series")
    series = cpi_manager.availible_cpi_series()
    st.table(series)

#Organizing dashboard layout
with col1:
    start_date, end_date = slider()    
    
with col2:
    region = region_selection()
    
with col3:
    item = item_selection()

plot_cpi(start_date, end_date, region, item)    

availible_series()
    


