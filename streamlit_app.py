# Import python packages
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

st.title("Customize Your Smoothie 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake connection (Streamlit-in-Snowflake)
cnx = st.connection("snowflake")
session = cnx.session()

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be:", name_on_order)

# Get fruit list
fruit_df = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

pd_df = fruit_df.to_pandas()

# Multiselect (must be a list, not a dataframe)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # SEARCH_ON value = lowercase fruit name
        search_on = fruit_chosen.lower()

        st.write(f"The search value for {fruit_chosen} is {search_on}.")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            response.json(),
            width="stretch"   # ✅ CORRECT replacement
        )

    # Insert order
    insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(insert_stmt).collect()
        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )
