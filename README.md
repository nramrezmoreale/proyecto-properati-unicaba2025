🏠 PROYECTO FINAL – PROGRAMACIÓN AVANZADA PARA CIENCIA DE DATOS
Universidad de la Ciudad de Buenos Aires — 2° Cuatrimestre 2025

Tema: Análisis predictivo del precio de propiedades en Argentina utilizando el dataset de Properati.

⸻

🎯 OBJETIVO
Desarrollar un modelo de regresión que prediga el precio de venta de propiedades en USD a partir de características como superficie, cantidad de ambientes y ubicación.

⸻

👥 INTEGRANTES DEL GRUPO

1️⃣ Nicolás Paul Ramírez Moreale — Data Engineer (Carga y Limpieza)
Descarga y exploración del dataset, limpieza de datos, manejo de nulos y outliers, creación del campo price_per_m2.

2️⃣ Camila Funes — Feature Engineer (Transformación)
Selección de variables, escalado (StandardScaler), codificación (OneHotEncoder), separación train/test.

3️⃣ Jose Ignacio Martinez — Modelador (Machine Learning)
Entrenamiento de al menos 2 modelos de regresión (Lineal y Random Forest), cálculo de métricas (RMSE, MAE, R²).

4️⃣ Guillermo Germán Jalil — Data Manager (Base de Datos)
Creación de base de datos SQLite, tablas (datos_entrada, resultados_modelo, config_modelo), conexión desde Python.

5️⃣ Sabrina Ianni Lucio — Data Visualizer (Visualización y Presentación)
Creación de gráficos con Matplotlib/Seaborn/Plotly, análisis comparativo de métricas, armado de presentación final.

⸻

📁 ESTRUCTURA DEL PROYECTO

```

📁 ESTRUCTURA DEL PROYECTO

proyecto-properati-ucb2025/
│
│   ├── preprocesamiento.ipynb    # Limpieza y exploración de datos
│   ├── entrenamiento_lineal.ipynb        # Entrenamiento y evaluación de modelo lineal
│   ├── entrenamiento_rforest.ipynb       # Entrenamiento y evaluación de modelo random forest
│	├── entrenamientos.ipynb       # Entrenamiento y evaluación de ambos modelos
│	├── resultados_lineal.csv y resultados_rforest.csv    # Resultado del entrenamiento y evaluación de ambos modelos
│	├── metricas_entrenamiento.csv    # Métricas del resultado del entrenamiento y evaluación de ambos modelos
│	├── db_data_loading    # Configuracion y carga de datos en la database
│	├── db_properati.db       # Base de datos resultante para análisis visual de los resultados

```


⸻

🧰 LIBRERÍAS PRINCIPALES
	•	pandas
	•	numpy
	•	scikit-learn
	•	matplotlib
	•	seaborn
	•	plotly
	•	sqlite3

⸻

📊 MÉTRICAS DEL MODELO
	•	RMSE (Root Mean Squared Error)
	•	MAE (Mean Absolute Error)
	•	R² (Coeficiente de determinación)

⸻

🗂️ DATASET
Dataset original: Properati Argentina (Kaggle)
https://www.kaggle.com/datasets/alejandroczernikier/properati-argentina-dataset

⸻

🚀 ENTREGA FINAL

El repositorio incluye:

✅ Código completo y notebooks ordenados
✅ Base de datos (properati.db)
✅ Archivos CSV (properati_clean.csv, metricas_modelos.csv)
✅ requirements.txt con dependencias
✅ README.md documentado
✅ Presentación final en PDF o PPTX
