import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# Carregar o dataset
data = pd.read_csv('arquivo.csv') #substituir pelo o arquivo

# Separar dados, marcas e categorias
X = data['Titulo']
y = data[['Marca', 'Categoria']]  # A nova coluna "Categoria" incluída aqui

# Pipeline de vetorização e classificação para múltiplas saídas
model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', MultiOutputClassifier(LogisticRegression()))
])

# Treinar o modelo
model.fit(X, y)

# Salvar o modelo
joblib.dump(model, 'ml_model_with_category.pkl')
print("Modelo treinado e salvo como ml_model_with_category.pkl")
