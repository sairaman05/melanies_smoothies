import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

st.title("Order a Smoothie 🥤")

session = get_active_session()

name_on_order = st.text_input("Your name")

fruit_df = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

ingredients = st.multiselect(
    "Choose up to 5 fruits",
    fruit_df
)

if st.button("Submit Order"):
    if not name_on_order or not ingredients:
        st.warning("Please enter your name and select fruits")
    else:
        ingredients_string = ", ".join(ingredients)

        insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS
        (NAME_ON_ORDER, INGREDIENTS)
        VALUES
        ('{name_on_order}', '{ingredients_string}')
        """

        session.sql(insert_stmt).collect()
        st.success("Your smoothie order has been placed! ✅")
