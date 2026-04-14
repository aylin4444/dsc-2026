# Streamlit application that interfaces with cars database
# running locally in MySQL

import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import pandas as pd
import os
import matplotlib.pyplot as plt   # added for bar chart

load_dotenv()

def connect_to_db():
    # DB_PASSWORD must be defined in .env.
    pw = os.environ.get('DB_PASSWORD')

    # Connect to DB
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password=pw,
      database="cars"
    )

    # Return database connection and cursor object for executing queries
    return mydb, mydb.cursor()

def close_connection(db, cursor):
    cursor.close()
    db.close()


def get_user_selections():
    with st.form(key='my_form'):
        retail_range = st.slider('Retail price ($)',
                        0, 100000, (20000, 50000))
        min_mpg = st.slider('Minimum fuel efficiency (highway - mpg)',
                        0, 55, 20)
        car_type = st.radio(
            'Car type',
            ('Sedan', 'Wagon', 'SUV', 'Sports Car')
        )
        submitted = st.form_submit_button(label='Process')

        if submitted:
            return retail_range, min_mpg, car_type
        else:
            return ((20000, 50000), 20, 'Sedan')


def exec_query(retail_range, min_mpg, car_type, cursor):
    # SQL query is broken down into multiple f strings for readibility.
    # f strings are concatenated automatically because of parenthesization.
    min_p, max_p = retail_range
    query = (f"SELECT Name, `Retail Price`, `Highway Miles Per Gallon`, Type"
             f" FROM cars WHERE `Retail Price` BETWEEN {min_p} AND {max_p}"
             f" AND `Highway Miles Per Gallon` > {min_mpg}"
             f" AND Type = '{car_type}';")
    print(query)
    # Execute the SQL query
    cursor.execute(query)

    # Put results in a DataFrame
    columns = [desc[0] for desc in cursor.description]
    results_df = pd.DataFrame(cursor.fetchall(), columns = columns)
    return results_df

def main():
    st.title('Car database')
    db, cursor = connect_to_db()
    
    # ---- Original app content ----
    retail_range, min_mpg, car_type = get_user_selections()
    results = exec_query(retail_range, min_mpg, car_type, cursor)
    st.markdown('---')
    st.subheader('Matches')
    st.dataframe(results, width = 900, height = 300)

    # ========== NEW FEATURE 1: Search by Car Make ==========
    st.markdown('---')
    st.header('🔍 Search by Car Make')
    with st.form('search_make_form'):
        search_term = st.text_input('Enter car make (e.g., Toyota, BMW)')
        search_submitted = st.form_submit_button('Search')
        if search_submitted and search_term:
            # Use the same cursor (but need to re-execute; cursor is still alive)
            # We'll use a separate query
            query_make = """
                SELECT Name, `Retail Price`, Type, `Highway Miles Per Gallon`
                FROM cars
                WHERE Name LIKE %s
            """
            cursor.execute(query_make, (f'%{search_term}%',))
            rows = cursor.fetchall()
            if rows:
                # Display as a table
                cols = ['Name', 'Retail Price', 'Type', 'Highway MPG']
                df_make = pd.DataFrame(rows, columns=cols)
                st.dataframe(df_make)
            else:
                st.info('No cars found with that make.')

    # ========== NEW FEATURE 2: Bar Chart - Avg MPG by Make ==========
    st.markdown('---')
    st.header('📊 Average Highway MPG by Car Make')
    # Get distinct car types from the table
    cursor.execute("SELECT DISTINCT Type FROM cars")
    types = [row[0] for row in cursor.fetchall()]
    if types:
        selected_type = st.selectbox('Choose car type', types)
        if st.button('Generate Chart'):
            # Query: average highway mpg per make (first word of Name)
            query_chart = """
                SELECT 
                    SUBSTRING_INDEX(Name, ' ', 1) AS Make,
                    AVG(`Highway Miles Per Gallon`) AS avg_mpg
                FROM cars
                WHERE Type = %s
                GROUP BY Make
                ORDER BY avg_mpg DESC
            """
            cursor.execute(query_chart, (selected_type,))
            data = cursor.fetchall()
            if data:
                makes = [row[0] for row in data]
                mpgs = [row[1] for row in data]
                fig, ax = plt.subplots()
                ax.barh(makes, mpgs, color='skyblue')
                ax.set_xlabel('Average Highway MPG')
                ax.set_title(f'Average MPG by Make for {selected_type}')
                st.pyplot(fig)
            else:
                st.info('No data available for the selected car type.')
    else:
        st.warning('No car types found in the database.')

    # ---- Close connection ----
    close_connection(db, cursor)

if __name__ == '__main__':
    main()
