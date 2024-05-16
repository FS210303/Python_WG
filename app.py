# Chat GPT wurde als Hilfsmittel für Teile des vorliegenden Codes benutzt. Dies ist mit einem (*) gekennzeichnet.

# Import der erforderlichen pip packages
import os
import streamlit as st
import pandas as pd
import requests

# Lesen vom Spoonacular API Key aus einer Umgebungsvariable (Security)
API_KEY = os.getenv("API_KEY")
# Definition der API Base URL
API_BASE_URL = "https://api.spoonacular.com"


def get_recipes(ingredients: list) -> dict:
    """Ruft Rezepte von der Spoonacular API ab.

    Args:
        ingredients: Eine Liste von Zutaten

    Returns:
        Rezepte als dict
    """
    # Globale Variable als workaround, da st.button (on_click=get_recipes) nichts zurückgibt
    global recipes_data
    recipes_data = []
    # Aufbereitung der Zutaten als URL Paramter für den API Aufruf
    ingredient_list = ingredients.split(',')
    ingredients_url_parameters = ',+'.join(ingredient_list)
    # Rezepte von der 'findByIngredients' API abrufen (*)
    response = requests.get(f"{API_BASE_URL}/recipes/findByIngredients?apiKey={API_KEY}&ingredients={ingredients_url_parameters}")
    # Wenn HTTP Status OK (200) JSON Antwort in Dict umwandeln
    if response.status_code == 200:
        recipes_data = response.json()
    else:
        recipes_data = "Something went wrong."


def format_amount_number(amount: float) -> str:
    """Rundet eine Gleitzahl auf zwei Dezimalstellen und gibt sie als String zurück

    Args:
        amount: Gleitzahl, die gerundet werden soll

    Returns:
        Gerundete Zahl als String.    
    """
    amount = round(amount,2)
    # Wenn Zahl gerade ist ohne Kommastellen
    if amount == int(amount):
        return str(int(amount))
    # Wenn Zahl ungerade ist mit Kommastellen
    else:
        return str(amount)


def create_ingredients_dataframe(people_count: int, recipe: list) -> pd.DataFrame:
    """Erstellt ein Dataframe für ein Rezept und der Anzahl der Personen

    Args:
        people_count: Anzahl Personen
        recipe: Rezept Liste von der Spoonacular API

    Returns:
        Pandas Dataframe (Grundlage für Charts)

    """
    data = {}
    # Aufbereitung der Daten der verwendeten Zutaten
    for ingredient in recipe["usedIngredients"]:
        name = ingredient['originalName']
        data[name] = people_count*ingredient['amount']

    # Aufbereitung der Daten der fehlenden Zutaten
    for ingredient in recipe["missedIngredients"]:
        name = ingredient['originalName']
        data[name] = people_count*ingredient['amount']
    
    # Erstellung vom Dataframe aus dem aufbereiteten data dict
    df = pd.DataFrame.from_dict(data, orient = 'index')
    df.rename(columns={0: 'Amount'}, inplace=True)
    df.index.name = 'Ingredient'
    return df




# Erstellung der Webapplikation

# Konfiguration der Streamlit-App, einschliesslich Titel, Beschreibung und Favicon. (*)
st.set_page_config(page_title="Recipe Finder", page_icon="ðŸ½ï¸")
st.title("Recipe Finder")
st.write("""Discover delicious recipes based on the ingredients you have on
            hand! Simply enter your ingredients and find suitable recipes for
            your next meal.""")

# Eingabefelder für die Anzahl der Personen und die Zutaten, sowie Searchbutton.
st.subheader("Input Ingredients separated by comma")
people_count = st.number_input("Number of people", min_value=1, max_value=100, step=1, value=1)
ingredients = st.text_input("Ingredients", placeholder="Flour, eggs, ...")
st.button("Search Recipes", on_click=get_recipes(ingredients))

if recipes_data:
    st.subheader("Recipes")

# Für jedes gefundene Rezept werden die Details angezeigt, einschliesslich der
# verwendeten Zutaten, fehlenden Zutaten und unverwendeten Zutaten. (*)
for recipe in recipes_data:
    used_ingredients = recipe["usedIngredients"]
    missed_ingredients = recipe["missedIngredients"]
    unused_ingredients = recipe["unusedIngredients"]

    if used_ingredients or missed_ingredients or unused_ingredients:
        st.markdown(f"<h4>{recipe['title']}</h4>", unsafe_allow_html=True)

    # Die Benutzeroberfläche ist in zwei Spalten aufgeteilt
    col1, col2 = st.columns([1, 2])
    # Linke Spalte enthält die verwendeten und fehlenden Zutaten
    with col1:
        # Auflistung der verwendeten Zutaten
        if used_ingredients:
            st.write("Ingredients used:")
            for ingredient in recipe["usedIngredients"]:
                amount_str = format_amount_number(people_count*ingredient['amount'])
                st.write(f"- {amount_str} {ingredient['unitLong']} {ingredient['originalName']}")
        
        # Auflistung der fehlenden Zutaten
        if missed_ingredients:
            st.write("Missing ingredients:")
            for ingredient in recipe["missedIngredients"]:
                amount_str = format_amount_number(people_count*ingredient['amount'])
                st.write(f"- {amount_str} {ingredient['unitLong']} {ingredient['originalName']}")

        # Auflistung der unverwendeten Zutaten
        if unused_ingredients:
            st.write("Ingredients not used:")
            for ingredient in recipe["unusedIngredients"]:
                amount_str = format_amount_number(people_count*ingredient['amount'])
                st.write(f"- {amount_str} {ingredient['unitLong']} {ingredient['originalName']}")

    # Rechte Spalte zeigt das  Bild des Rezepts und ein Balkendiagramm mit den Zutaten. (*)
    with col2:
        st.image(recipe["image"], caption=recipe["title"], use_column_width=True)
        st.bar_chart(create_ingredients_dataframe(people_count, recipe))
