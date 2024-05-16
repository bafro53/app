import streamlit as st
st.title ("hellllooooo")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Charger les données
data = pd.read_csv('Bakery sales.csv')
data.drop(columns=["Unnamed: 0"], inplace=True)

# Afficher les données
st.write(data)
st.write(data.head())
st.write(data.info())

# Nettoyage des données
word_list = ["NaN", "-", "nan", "NAN", "None", "NONE", "none", " ", "_", "."]
found = []

for word in word_list:
    if data['article'].str.contains(word).any():
        found.append(word)
st.write(found)

count_none = data[data['article'] == 'NONE'].shape[0]
st.write(count_none)

data_clean = data[~data['article'].isin(word_list)]
st.write(data_clean.describe())

# Articles uniques
ARTICLES = pd.unique(data["article"])
st.write(ARTICLES)
st.write(len(ARTICLES))

# Conversion des colonnes de date et heure
data_clean['time'] = pd.to_datetime(data_clean['time']).dt.time
data_clean['date'] = pd.to_datetime(data_clean['date'])
data_clean['unit_price'] = data_clean['unit_price'].str.replace(' €', '').str.replace(',', '.').astype(float)

st.write(data_clean)

# Ajout de l'année
data_clean['Year'] = pd.to_datetime(data_clean['date']).dt.year
summary_data = data_clean.groupby(['date', 'article']).size().reset_index(name='Count')
summary_data['Year'] = pd.to_datetime(summary_data['date']).dt.year

# Graphique des transactions totales par date
plt.figure(figsize=(10, 6))
for year, color in zip(summary_data['Year'].unique(), ["coral", "cornflowerblue"]):
    subset = summary_data[summary_data['Year'] == year]
    plt.plot(subset['date'], subset['Count'], label=year, color=color)

plt.title('Total Transactions by Date')
plt.xlabel('Date')
plt.ylabel('Transactions')
plt.legend(title='Year', loc='lower center')
plt.grid(True)
st.pyplot(plt)

# Ventes quotidiennes
daily_sales = data_clean.groupby(data_clean['date'].dt.date).size()

plt.figure(figsize=(12, 6))
plt.plot(daily_sales.index, daily_sales.values, color='coral')
plt.title('Total Daily Sales')
plt.xlabel('Date')
plt.ylabel('Total Sales')
plt.grid(True)
st.pyplot(plt)

# Articles vendus par jour
articles_par_jour = data_clean.groupby('date').agg({'Quantity': 'sum'})

plt.figure(figsize=(12, 6))
articles_par_jour['Quantity'].plot()
plt.title('Nombre d\'articles vendus par jour')
plt.xlabel('Date')
plt.ylabel('Nombre d\'articles')
st.pyplot(plt)

# Clients par jour
clients_par_jour = data_clean.groupby('date')['ticket_number'].nunique()

plt.figure(figsize=(12, 6))
clients_par_jour.plot()
plt.title('Nombre de clients différents par jour')
plt.xlabel('Date')
plt.ylabel('Nombre de clients')
st.pyplot(plt)

# Montant moyen du panier
data_clean['Total'] = data_clean['Quantity'] * data_clean['unit_price']
panier_moyen = data_clean.groupby('ticket_number')['Total'].sum().mean()
st.write("Le montant moyen du panier est de:", panier_moyen, "€")

# Ventes mensuelles
data_clean['Year_Month'] = data_clean['date'].dt.to_period('M')
monthly_sales = data_clean.groupby('Year_Month')['Total'].sum()

plt.figure(figsize=(10, 6))
monthly_sales.plot(kind='bar')
plt.title('Nombre d\'articles vendus chaque mois')
plt.xlabel('Mois')
plt.ylabel('Nombre d\'articles vendus')
st.pyplot(plt)

# Ventes par jour de la semaine
data_clean['Day_of_week'] = data_clean['date'].dt.day_name()
ventes_par_jour_semaine = data_clean.groupby('Day_of_week')['article'].count()

plt.figure(figsize=(10, 6))
ventes_par_jour_semaine.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).plot(kind='bar')
plt.title('Nombre d\'articles vendus selon le jour de la semaine')
plt.xlabel('Jour de la semaine')
plt.ylabel('Nombre d\'articles vendus')
st.pyplot(plt)

# Ventes par article
ventes_par_article = data_clean.groupby('article')['Quantity'].sum()

plt.figure(figsize=(12, 6))
ventes_par_article.sort_values(ascending=False).plot(kind='bar')
plt.title('Nombre de produits vendus pour chaque article unique')
plt.xlabel('Article')
plt.ylabel('Nombre d\'articles vendus')
plt.xticks(rotation=45, ha='right')
st.pyplot(plt)

# Articles représentant 80% des ventes totales
ventes_totales = data_clean['Quantity'].sum()
ventes_par_article = data_clean.groupby('article')['Quantity'].sum().sort_values(ascending=False)
ventes_cumulatives = ventes_par_article.cumsum()
seuil_80 = ventes_totales * 0.8
articles_80 = ventes_par_article[ventes_cumulatives <= seuil_80]

plt.figure(figsize=(12, 6))
articles_80.plot(kind='bar')
plt.title('Articles représentant 80% des ventes totales')
plt.xlabel('Article')
plt.ylabel('Nombre d\'articles vendus')
plt.xticks(rotation=45, ha='right')
st.pyplot(plt)

st.write("Articles représentant 80% des ventes totales :\n", articles_80)

# Chiffre d'affaires par article
ca_totale = (data_clean['Quantity'] * data_clean['unit_price']).sum()
ca_par_article = (data_clean.groupby('article')
                  .apply(lambda x: (x['Quantity'] * x['unit_price']).sum())
                  .sort_values(ascending=False))
ca_cumulatif = ca_par_article.cumsum()
seuil_80_ca = ca_totale * 0.8
articles_80_ca = ca_par_article[ca_cumulatif <= seuil_80_ca]

plt.figure(figsize=(12, 6))
articles_80_ca.plot(kind='bar')
plt.title('Articles représentant 80% du chiffre d\'affaires total')
plt.xlabel('Article')
plt.ylabel('Chiffre d\'affaires (€)')
plt.xticks(rotation=45, ha='right')
st.pyplot(plt)

st.write("Articles représentant 80% du chiffre d'affaires total :\n", articles_80_ca)

# Corrélation des ventes entre produits
data_top_products = data_clean[data_clean['article'].isin(articles_80_ca.index)]
corr_matrix = data_top_products.pivot_table(index='ticket_number', columns='article', values='Quantity', fill_value=0)
correlation = corr_matrix.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation, annot=True, cmap='coolwarm')
plt.title('Corrélation de ventes entre produits')
st.pyplot(plt)

top_10_corr = (correlation.unstack()
               .sort_values(ascending=False)
               .drop_duplicates()
               .head(20))
st.write("Top 10 des plus hautes corrélations entre produits :\n", top_10_corr)

# Transactions par heure
data_clean['hour'] = data_clean['time'].apply(lambda x: x.hour)
transactions_par_heure = data_clean.groupby('hour').size()

plt.figure(figsize=(12, 6))
transactions_par_heure.plot(kind='bar', color='skyblue')
plt.title('Répartition des transactions par heure')
plt.xlabel('Heure de la journée')
plt.ylabel('Nombre de transactions')
plt.xticks(rotation=0)
plt.grid(axis='y', linestyle='--', alpha=0.7)
st.pyplot(plt)

# Corrélation des ventes des principaux articles par jour de la semaine
plt.figure(figsize=(10, 8))
correlation_matrix = data_top_products.pivot_table(index='article', columns='Day_of_week', values='Quantity', aggfunc='sum')

sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Corrélation des ventes des principaux articles par jour de la semaine')
plt.xlabel('Jour de la semaine')
plt.ylabel('Jour de la semaine')
st.pyplot(plt)

top_10_corr_day = (correlation_matrix.unstack()
               .sort_values(ascending=False)
               .drop_duplicates()
               .head(20))
st.write("Top 10 des plus hautes corrélations entre produits :\n", top_10_corr_day)

# Ventes par jour de la semaine pour un produit spécifique
produit_df = data_clean[data_clean['article']=='TRADITIONAL BAGUETTE']
ventes_par_jour_semaine_produit = produit_df.groupby('Day_of_week')['Quantity'].count()
st.write(ventes_par_jour_semaine_produit)

plt.figure(figsize=(10, 6))
ventes_par_jour_semaine_produit.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).plot(kind='bar')
plt.title('Nombre d\'articles vendus selon le jour de la semaine')
plt.xlabel('Jour de la semaine')
plt.ylabel('Nombre d\'articles vendus')
st.pyplot(plt)
