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

# Get fruit data INCLUDING SEARCH_ON
fruit_df = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert to pandas
pd_df = fruit_df.to_pandas()

# Multiselect must use a list
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Use SEARCH_ON column (LAB REQUIREMENT)
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for",
            fruit_chosen,
            "is",
            search_on
        )

        st.subheader(f"{fruit_chosen} Nutrition Information")

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            response.json(),
            width="stretch"
        )

    # Insert order only if name exists
    if st.button("Submit Order"):
        if not name_on_order:
            st.warning("Please enter a name for your smoothie.")
        else:
            insert_stmt = f"""
                INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
                VALUES ('{ingredients_string.strip()}', '{name_on_order}')
            """

            session.sql(insert_stmt).collect()
            st.success(
                f"Your Smoothie is ordered, {name_on_order}! ✅"
            )
