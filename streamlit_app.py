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

# Get fruit list (ONLY columns that exist)
fruit_df = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

pd_df = fruit_df.to_pandas()

# Multiselect MUST use a list, not a dataframe
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # SEARCH_ON is simply lowercase fruit name
        search_on = fruit_chosen.lower()

        st.write(
            f"The search value for {fruit_chosen} is {search_on}."
        )

        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(response.json(), use_container_width=True)

    # Insert order
    insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{ingredients_string.strip()}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(insert_stmt).collect()
        st.success(
            f"Your Smoothie is ordered, {name_on_order}!",
            icon="✅"
        )


import request
smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width = True)
