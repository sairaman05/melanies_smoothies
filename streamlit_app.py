import streamlit as st
import snowflake.connector
import pandas as pd

st.title("Order a Smoothie 🥤")

# Create Snowflake connection
conn = snowflake.connector.connect(
    account=st.secrets["snowflake"]["account"],
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"],
    role=st.secrets["snowflake"]["role"]
)

cursor = conn.cursor()

# Customer name
name_on_order = st.text_input("Your name")

# Load fruit options
cursor.execute("SELECT FRUIT_NAME FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
fruit_df = pd.DataFrame(cursor.fetchall(), columns=["FRUIT_NAME"])

ingredients = st.multiselect(
    "Choose up to 5 fruits",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# Submit order
if st.button("Submit Order"):
    if not name_on_order or not ingredients:
        st.warning("Please enter your name and select fruits")
    else:
        ingredients_string = ", ".join(ingredients)

        insert_sql = """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS (NAME_ON_ORDER, INGREDIENTS)
            VALUES (%s, %s)
        """

        cursor.execute(insert_sql, (name_on_order, ingredients_string))
        conn.commit()

        st.success("Your smoothie order has been placed! ✅")

# Cleanup
cursor.close()
conn.close()
