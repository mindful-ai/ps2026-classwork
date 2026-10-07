import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

st.title("Upload Data for EDA")
file = st.file_uploader("Upload a CSV file", type="csv")
if file:
    data = pd.read_csv(file)
    st.write("Data Preview:", data.head())
    st.write("Basic Statistics:", data.describe())

    st.title("Data Visualization")
    feature = st.selectbox("Select a feature to visualize", data.columns)
    plt.figure()
    sns.histplot(data[feature], kde=True)
    st.pyplot(plt)

'''

This app lets users upload a dataset and displays the first few rows and summary statistics. 
It introduces st.file_uploader() for file handling and st.write() for data display.
'''