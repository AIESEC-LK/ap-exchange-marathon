import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import json  # Import the json module
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Loading Data
@st.cache_data(ttl=5)  ## time to live - you can change this as it is required to be refereshed
def load_data(sheet_url):
    try:
        data = pd.read_csv(sheet_url)
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Function to create a bar chart based on the specified metric
def create_bar_chart_seperate(df, entity, metric, title):
    filtered_df = df[df['Entity'] == entity]
    fig = px.bar(filtered_df, x='Function', y=metric, title=title, labels={'Function': 'Function', 'Entity': 'Entity', metric: metric}, color='Function')
    return fig

# Function to create a bar chart based on the total points of each entity
def create_bar_chart(entity_sum):
    # Convert entity sum dictionary to DataFrame
    df_entity_sum = pd.DataFrame.from_dict(entity_sum, orient='index')
    
    # Reset index to make entity a column instead of index
    df_entity_sum.reset_index(inplace=True)
    df_entity_sum.rename(columns={'index': 'Entity'}, inplace=True)
    
    # Create a bar chart using Plotly Express
    fig = px.bar(df_entity_sum, x='Entity', y='Total', title='Total Score', labels={'Entity': 'Entity', 'Total': 'Total Points'}, color='Entity')

            # Hide the legend
    fig.update_layout(showlegend=False)
    
    return fig

# Function to calculate the total 'Applied' related to each entity
def calculate_total_applied(df):
    entity_applied_total = {}
    for index, row in df.iterrows():
        entity = row['Entity']
        applied = row['Applied']
        if entity not in entity_applied_total:
            entity_applied_total[entity] = applied
        else:
            entity_applied_total[entity] += applied
    return entity_applied_total

# Function to calculate the total 'Approved' related to each entity
def calculate_total_approved(df):
    entity_approved_total = {}
    for index, row in df.iterrows():
        entity = row['Entity']
        approved = row['Approved']
        if entity not in entity_approved_total:
            entity_approved_total[entity] = approved
        else:
            entity_approved_total[entity] += approved
    return entity_approved_total

# Function to calculate the count of 'Applied' related to each entity based on the selected function
def count_applied_by_entity(df, selected_function):
    filtered_df = df[df['Function'] == selected_function]
    applied_counts = filtered_df.groupby('Entity')['Applied'].sum().reset_index()
    applied_counts.rename(columns={'Applied': 'Count_Applied'}, inplace=True)
    return applied_counts

# Function to calculate the count of 'Approved' related to each entity based on the selected function
def count_approved_by_entity(df, selected_function):
    filtered_df = df[df['Function'] == selected_function]
    approved_counts = filtered_df.groupby('Entity')['Approved'].sum().reset_index()
    approved_counts.rename(columns={'Approved': 'Count_Approved'}, inplace=True)
    return approved_counts

icon_path = 'https://aiesec.lk/data/dist/images/favicon.png'

def calculate_approval_ranks(df):
    # Sort the DataFrame by 'Total_Approved' column in descending order
    df_sorted = df.sort_values(by='Total_Approved', ascending=False)
    # Add a new column 'Rank' to store the ranks
    df_sorted['Rank'] = range(1, len(df_sorted) + 1)
    
    return df_sorted

def display_leaderboard(df, total_approvals):
    
    
    # Define a layout with two columns
    col1, col2 = st.columns([4, 1])

    # Display the total approvals in the first column
    with col1:
        st.subheader('Leaderboard')

    # Display the leaderboard in the second column
    with col2:
        # st.metric(label="Total AP Approvals", value=total_approvals)
        # st.button(f"Total AP Approvals : **{total_approvals}**", key="no_action_button")
        st.metric(label="Total AP Approvals", value=total_approvals)
    st.dataframe(df.set_index('Rank'), use_container_width=True, height=250)

def display_approval_ranks(df):
    # Calculate ranks
    df_with_ranks = calculate_approval_ranks(df)
    
    # Drop the index column
    df_without_index = df_with_ranks[['Rank', 'Entity', 'Total_Approved']]
    # Rename the column 'Total_Approved' to 'Total Approvals'
    df_with_ranks.rename(columns={'Total_Approved': 'Total Approvals'}, inplace=True)

    
    # Apply gold, silver, and bronze medals to the 'Entity' column
    df_with_ranks['Entity'] = df_with_ranks.apply(lambda row: 
                                                   f"🥇 {row['Entity']}" if row['Rank'] == 1 else 
                                                   f"🥈 {row['Entity']}" if row['Rank'] == 2 else 
                                                   f"🥉 {row['Entity']}" if row['Rank'] == 3 else 
                                                   row['Entity'], axis=1)
    
    # Calculate the total of the 'Total Approvals' column
    tot_ap_approvals = df_with_ranks['Total Approvals'].sum()

    #display the leaderboard section
    display_leaderboard(df_with_ranks, tot_ap_approvals)


# Main Streamlit app
def main():
    st.set_page_config(
    layout="centered",
    ## You can change the page title here
    page_title="AP Hackathon - Dashboard",
    page_icon= icon_path,
    )   

    ## The Dashboard Title (You can change here)
    st.title("AP Hackathon - Dashboard")

    st_autorefresh(interval=30 * 1000, key="data_refresh")  # Set interval to 5 minutes
    # URL to your Google Sheets data
    ## Datasource url / Google Sheets CSV
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRQ0DK7DqYpQQwLsb93-fbhDN1NhHLO9P7GNhyceIwWdj5EOFInWSflTbvDYrakkuEJlDHgDV25kP9w/pub?gid=1562137798&single=true&output=csv"

    # Load data using the cached function
    data = load_data(sheet_url)

    if data is not None:

        # Check if the 'Entity' column exists in the DataFrame
        if 'Entity' in data.columns:

            # Calculate total 'Applied' related to each entity
            entity_applied_total = calculate_total_applied(data)

            # Convert dictionary to DataFrame
            df_entity_applied_total = pd.DataFrame.from_dict(entity_applied_total, orient='index', columns=['Total_Applied'])
            df_entity_applied_total.reset_index(inplace=True)
            df_entity_applied_total.rename(columns={'index': 'Entity'}, inplace=True)
            
            # Create a colored bar chart using Plotly Express
            fig = px.bar(df_entity_applied_total, x='Entity', y='Total_Applied', title='Total Applications by Entity', labels={'Entity': 'Entity', 'Total_Applied': 'Applications'}, color='Entity')

            # Hide the legend
            fig.update_layout(showlegend=False)

            # Use the function to display the ranks table
            
            # Calculate total 'Approved' related to each entity
            entity_approved_total = calculate_total_approved(data)

            # Convert dictionary to DataFrame
            df_entity_approved_total = pd.DataFrame.from_dict(entity_approved_total, orient='index', columns=['Total_Approved'])
            df_entity_approved_total.reset_index(inplace=True)
            df_entity_approved_total.rename(columns={'index': 'Entity'}, inplace=True)
            display_approval_ranks(df_entity_approved_total)
            # Create a colored bar chart using Plotly Express
            fig_approved = px.bar(df_entity_approved_total, x='Entity', y='Total_Approved', title='Total Approvals by Entity', labels={'Entity': 'Entity', 'Total_Approved': 'Approvals'},color='Entity')
            # Hide the legend
            fig_approved.update_layout(showlegend=False)

            st.plotly_chart(fig_approved, use_container_width=True)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader('Functional Analysis')
            # Create a select box to choose the 'Function'
            selected_function = st.selectbox('Select Function', data['Function'].unique())
            
            # Get the count of 'Applied' related to each entity based on the selected function
            applied_counts = count_applied_by_entity(data, selected_function)

            # Create a bar chart using Plotly Express
            fig_1 = px.bar(applied_counts, x='Entity', y='Count_Applied', title=f'Applications by Entity for {selected_function} Function',labels={'Entity': 'Entity', 'Count_Applied': 'Applications'}, color='Entity')
            fig_1.update_layout(showlegend=False)


            # Get the count of 'Approved' related to each entity based on the selected function
            approved_counts = count_approved_by_entity(data, selected_function)

            # Create a bar chart using Plotly Express
            fig_2 = px.bar(approved_counts, x='Entity', y='Count_Approved', title=f'Approvals by Entity for {selected_function} Function',labels={'Entity': 'Entity', 'Count_Approved': 'Approvals'}, color='Entity')
            fig_2.update_layout(showlegend=False)
            
            st.plotly_chart(fig_2, use_container_width=True)
            st.plotly_chart(fig_1, use_container_width=True)
            
            
            st.write("<br><br>", unsafe_allow_html=True)
            #Footer - It would be great if you could give us a recognition for the team.
            st.write("<p style='text-align: center;'>Made with ❤️ by &lt;/Dev.Team&gt; of <strong>AIESEC in Sri Lanka</strong></p>", unsafe_allow_html=True)

        else:
            st.error("The 'Entity' column does not exist in the loaded data.")
    else:
        st.error("Failed to load data.")

if __name__ == "__main__":
    main()
