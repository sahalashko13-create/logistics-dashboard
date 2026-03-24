import streamlit as st
import pandas as pd
import networkx as nx
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

# Налаштування сторінки
st.set_page_config(page_title="Logistics Dashboard", layout="wide")

st.title("🚛 Оптимізація логістичних маршрутів")

# 1. Завантаження даних
try:
    df = pd.read_csv('data.csv')
    
    # Бічна панель
    st.sidebar.header("Налаштування маршруту")
    locations = sorted(list(set(df['start'].unique()) | set(df['end'].unique())))
    
    start_point = st.sidebar.selectbox("Точка відправлення", locations)
    end_point = st.sidebar.selectbox("Точка призначення", locations)
    
    # 2. Побудова графа
    G = nx.from_pandas_edgelist(df, 'start', 'end', ['distance', 'cost'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Найкоротший шлях")
        if st.button("Розрахувати маршрут"):
            try:
                path = nx.shortest_path(G, source=start_point, target=end_point, weight='distance')
                distance = nx.shortest_path_length(G, source=start_point, target=end_point, weight='distance')
                
                st.success(f"Маршрут знайдено!")
                st.write(f"**Шлях:** {' ➡️ '.join(path)}")
                st.info(f"**Загальна відстань:** {distance} км")
            except nx.NetworkXNoPath:
                st.error("Маршрут між цими точками неможливий")

    with col2:
        st.subheader("📊 Візуалізація мережі")
        fig, ax = plt.subplots()
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, font_weight='bold')
        st.pyplot(fig)

    # 3. Карта (Folium)
    st.subheader("🗺️ Інтерактивна карта об'єктів")
    # Створюємо базову карту (центруємо на першій точці)
    m = folium.Map(location=[50.45, 30.52], zoom_start=6) 
    st.info("Тут відображається карта мережі складів")
    folium_static(m)

except Exception as e:
    st.error(f"Помилка завантаження даних: {e}")
    st.info("Перевірте, чи файл data.csv завантажений на GitHub.")
