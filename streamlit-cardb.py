import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Create an in-memory SQLite database and load sample data
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE cars (
    Name TEXT,
    `Retail Price` REAL,
    `Highway Miles Per Gallon` INTEGER,
    Type TEXT,
    Make TEXT
)
''')

sample_cars = [
    ('Toyota Camry', 28000, 38, 'Sedan', 'Toyota'),
    ('Honda Accord', 27000, 36, 'Sedan', 'Honda'),
    ('Toyota RAV4', 35000, 35, 'SUV', 'Toyota'),
    ('Honda CR-V', 34000, 34, 'SUV', 'Honda'),
    ('BMW X5', 65000, 25, 'SUV', 'BMW'),
    ('Ford Mustang', 45000, 25, 'Sports Car', 'Ford'),
    ('Chevrolet Corvette', 70000, 24, 'Sports Car', 'Chevrolet'),
    ('Tesla Model 3', 50000, 130, 'Sedan', 'Tesla')
]

cursor.executemany('INSERT INTO cars VALUES (?,?,?,?,?)', sample_cars)
conn.commit()

st.title('Car Database')

# ----- FEATURE 1: Search by Car Make -----
st.header('🔍 Search by Car Make')
search_term = st.text_input('Enter car make (e.g., Toyota, BMW)')
if st.button('Search'):
    if search_term:
        query = "SELECT Name, `Retail Price`, Type, `Highway Miles Per Gallon` FROM cars WHERE Make LIKE ?"
        df = pd.read_sql_query(query, conn, params=(f'%{search_term}%',))
        if not df.empty:
            st.dataframe(df)
        else:
            st.info('No cars found')

# ----- FEATURE 2: Bar Chart of Avg MPG by Make -----
st.header('📊 Average Highway MPG by Car Make')
cursor.execute("SELECT DISTINCT Type FROM cars")
types = [row[0] for row in cursor.fetchall()]
selected_type = st.selectbox('Choose car type', types)
if st.button('Generate Chart'):
    query = "SELECT Make, AVG(`Highway Miles Per Gallon`) as avg_mpg FROM cars WHERE Type = ? GROUP BY Make ORDER BY avg_mpg DESC"
    df = pd.read_sql_query(query, conn, params=(selected_type,))
    if not df.empty:
        fig, ax = plt.subplots()
        ax.barh(df['Make'], df['avg_mpg'], color='skyblue')
        ax.set_xlabel('Average Highway MPG')
        ax.set_title(f'Average MPG by Make for {selected_type}')
        st.pyplot(fig)
    else:
        st.info('No data')
