import streamlit as st
import pandas as pd
import networkx as nx
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

# 1. Налаштування сторінки
st.set_page_config(page_title="Панель логістики v1.0", layout="wide", page_icon="🚛")

# Стилізація заголовку
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; color: #31333F; }
    .stAlert { padding: 0.5rem 1rem; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="big-font">🚛 5. Панель моніторингу логістичних даних</p>', unsafe_allow_html=True)

# 2. Завантаження даних з перевіркою (Вимога: CSV)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv')
        # Перевірка наявності необхідних колонок
        required_cols = ['start', 'end', 'distance', 'cost', 'time_hours', 'start_lat', 'start_lon', 'end_lat', 'end_lon']
        if not all(col in df.columns for col in required_cols):
            st.error("Помилка: У файлі data.csv не вистачає необхідних колонок (координат або часу).")
            st.stop()
        return df
    except FileNotFoundError:
        st.error("Помилка: Файл 'data.csv' не знайдено на GitHub. Будь ласка, завантажте його.")
        st.stop()

df = load_data()

# 3. Побудова графа мережі
G = nx.from_pandas_edgelist(df, 'start', 'end', ['distance', 'cost', 'time_hours'])
locations = sorted(list(G.nodes()))

# БІЧНА ПАНЕЛЬ (НАЛАШТУВАННЯ)
st.sidebar.markdown("### 🛠️ Управління маршрутом")
start_point = st.sidebar.selectbox("🚩 Точка відправлення", locations)
end_point = st.sidebar.selectbox("🏁 Точка призначення", locations)

# Вибір критерію оптимізації
opt_criterion = st.sidebar.radio("🎯 Оптимізувати за:", ("Відстанню", "Вартістю", "Часом"))
criteria_map = {"Відстанню": "distance", "Вартістю": "cost", "Часом": "time_hours"}
selected_weight = criteria_map[opt_criterion]

calc_btn = st.sidebar.button("🚀 Розрахувати оптимальний шлях", use_container_width=True)

# ОСНОВНА ПАНЕЛЬ
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🗺️ Маршрут на карті (Dijkstra)")
    
    # Створення карти (фокусуємося на Києві)
    map_center = [50.45, 30.52] 
    m = folium.Map(location=map_center, zoom_start=6, tiles="OpenStreetMap")
    
    # Додавання всіх точок на карту (Вимога: Пункти доставки)
    # Збираємо унікальні точки та їх координати
    nodes_df = pd.concat([
        df[['start', 'start_lat', 'start_lon']].rename(columns={'start':'name', 'start_lat':'lat', 'start_lon':'lon'}),
        df[['end', 'end_lat', 'end_lon']].rename(columns={'end':'name', 'end_lat':'lat', 'end_lon':'lon'})
    ]).drop_duplicates()
    
    for _, row in nodes_df.iterrows():
        icon_color = 'red' if row['name'] == 'Sklad' else 'blue'
        icon_type = 'cloud' if row['name'] == 'Sklad' else 'shopping-cart'
        
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=f"📍 {row['name']}",
            icon=folium.Icon(color=icon_color, icon=icon_type)
        ).add_to(m)

    # ЛОГІКА РОЗРАХУНКУ МАРШРУТУ
    if calc_btn:
        try:
            # Використання алгоритму Dijkstra (nx.shortest_path з вагою)
            path = nx.shortest_path(G, source=start_point, target=end_point, weight=selected_weight)
            
            # Розрахунок підсумків
            path_edges = list(zip(path, path[1:]))
            total_dist = sum(G[u][v]['distance'] for u, v in path_edges)
            total_cost = sum(G[u][v]['cost'] for u, v in path_edges)
            total_time = sum(G[u][v]['time_hours'] for u, v in path_edges)
            
            # Відображення результатів (вимога Dijkstra)
            st.success(f"**Алгоритм Dijkstra знайшов оптимальний шлях!**")
            st.markdown(f"🏆 **Найкращий маршрут ({opt_criterion}):** <br> {' ➡️ '.join([f'<b>{node}</b>' for node in path])}", unsafe_allow_html=True)
            
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            summary_col1.metric("📏 Відстань", f"{total_dist} км")
            summary_col2.metric("💰 Витрати", f"{total_cost} грн")
            summary_col3.metric("⏱️ Час", f"{total_time} год")

            # Малювання маршруту на карті
            path_coords = []
            for node in path:
                # Знаходимо координати вузла
                node_data = nodes_df[nodes_df['name'] == node].iloc[0]
                path_coords.append([node_data['lat'], node_data['lon']])
            
            # Малюємо лінію маршруту
            folium.PolyLine(
                locations=path_coords,
                color="red",
                weight=5,
                opacity=0.8,
                tooltip=f"Маршрут: {opt_criterion}"
            ).add_to(m)

        except nx.NetworkXNoPath:
            st.error(f"⚠️ На жаль, маршрут між {start_point} та {end_point} неможливий.")
        except Exception as e:
            st.error(f"⚠️ Виникла непередбачувана помилка: {e}")

    # Відображення карти
    folium_static(m, width=1000, height=500)

with col2:
    st.markdown("### 📊 Побудуй графіки часу/витрат")
    
    # Вибір типу графіка
    chart_type = st.radio("Оберіть дані для порівняння:", ("Відстань vs Вартість", "Відстань vs Час"))
    
    if chart_type == "Відстань vs Вартість":
        fig, ax = plt.subplots(figsize=(6, 5))
        df_sorted = df.sort_values(by='distance')
        ax.plot(df_sorted['distance'], df_sorted['cost'], marker='o', linestyle='-', color='#1f77b4', linewidth=2)
        ax.set_title("Залежність витрат від відстані")
        ax.set_xlabel("Відстань (км)")
        ax.set_ylabel("Вартість (грн)")
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)
        
    else:
        fig, ax = plt.subplots(figsize=(6, 5))
        df_sorted = df.sort_values(by='distance')
        ax.plot(df_sorted['distance'], df_sorted['time_hours'], marker='s', linestyle='-', color='#ff7f0e', linewidth=2)
        ax.set_title("Залежність часу від відстані")
        ax.set_xlabel("Відстань (км)")
        ax.set_ylabel("Час (год)")
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

    st.markdown("---")
    st.info("📊 Графіки побудовані на основі всіх доступних маршрутів у CSV.")
