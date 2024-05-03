import os
import streamlit as st
import pandas as pd
import requests


API_KEY = os.getenv("API_KEY")
API_BASE_URL = "https://api.spoonacular.com"


def get_recipes(ingredients: list) -> dict:
    # Use global variable as st.button onclick doesn't return data
    global recipes_data
    recipes_data = []
    # Prepare ingredient list for api request
    ingredient_list = ingredients.split(',')
    ingredients_url_parameters = ',+'.join(ingredient_list)
    # Get recipes from findByIngredients api endpoint
    response = requests.get(f"{API_BASE_URL}/recipes/findByIngredients?apiKey={API_KEY}&ingredients={ingredients_url_parameters}")
    # Return result as dict if http status 200
    if response.status_code == 200:
        recipes_data = response.json()
    else:
        recipes_data = "Something went wrong."


def format_amount_number(amount: float) -> str:
    amount = round(amount,2)
    if amount == int(amount):
        return str(int(amount))
    else:
        return str(amount)


def create_ingredients_dataframe(people_count: int, recipe: list) -> pd.DataFrame:
    # Create pandas dataframe for barchart
    data = {}
    for ingredient in recipe["usedIngredients"]:
        name = ingredient['originalName']
        data[name] = people_count*ingredient['amount']

    for ingredient in recipe["missedIngredients"]:
        name = ingredient['originalName']
        data[name] = people_count*ingredient['amount']
    df = pd.DataFrame.from_dict(data, orient = 'index')
    # Rename columns for frontend
    df.rename(columns={0: 'Amount'}, inplace=True)
    df.index.name = 'Ingredient'
    return df


# Setup page
st.set_page_config(page_title="Recipe Finder", page_icon="🍽️")
st.title("Recipe Finder")
st.write("""Discover delicious recipes based on the ingredients you have on
            hand! Simply enter your ingredients and find suitable recipes for
            your next meal.""")

# Ingredients and people Input and search button
st.subheader("Input Ingredients separated by comma")
people_count = st.number_input("Number of people", min_value=1, max_value=100, step=1, value=1)
ingredients = st.text_input("Ingredients", placeholder="Flour, eggs, ...")
st.button("Search Recipes", on_click=get_recipes(ingredients))

if recipes_data:
    st.subheader("Recipes")

for recipe in recipes_data:
    used_ingredients = recipe["usedIngredients"]
    missed_ingredients = recipe["missedIngredients"]
    unused_ingredients = recipe["unusedIngredients"]

    if used_ingredients or missed_ingredients or unused_ingredients:
        st.markdown(f"<h4>{recipe['title']}</h4>", unsafe_allow_html=True)

    # Ingredients area
    col1, col2 = st.columns([1, 2])
    with col1:
        if used_ingredients:
            st.write("Ingredients used:")
            for ingredient in recipe["usedIngredients"]:
                amount_str = format_amount_number(people_count*ingredient['amount'])
                st.write(f"- {amount_str} {ingredient['unitLong']} {ingredient['originalName']}")

        if missed_ingredients:
            st.write("Missing ingredients:")
            for ingredient in recipe["missedIngredients"]:
                amount_str = format_amount_number(people_count*ingredient['amount'])
                st.write(f"- {amount_str} {ingredient['unitLong']} {ingredient['originalName']}")

        if unused_ingredients:
            st.write("Ingredients not used:")
            for ingredient in recipe["unusedIngredients"]:
                amount_str = format_amount_number(people_count*ingredient['amount'])
                st.write(f"- {amount_str} {ingredient['unitLong']} {ingredient['originalName']}")

    # Image area
    with col2:
        st.image(recipe["image"], caption=recipe["title"], use_column_width=True)
        st.bar_chart(create_ingredients_dataframe(people_count, recipe))
