import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import folium

# --- 1. ЗАВАНТАЖЕННЯ ДАНИХ (CSV) ---
df = pd.read_csv('data.csv')
print("✅ Дані завантажено!")

# --- 2. АЛГОРИТМ ДЕЙКСТРИ (Оптимальний маршрут) ---
G = nx.Graph()
for _, row in df.iterrows():
    G.add_edge(row['start'], row['end'], weight=row['distance'])

start_p, end_p = 'Sklad', 'Magazin_3'
path = nx.dijkstra_path(G, start_p, end_p, weight='weight')
length = nx.dijkstra_path_length(G, start_p, end_p, weight='weight')

print(f"📍 Найкращий маршрут: {' -> '.join(path)}")
print(f"📏 Довжина шляху: {length} км")

# --- 3. ГРАФІКИ ВИТРАТ (Аналітика) ---
plt.figure(figsize=(8, 4))
plt.bar(df['end'], df['cost'], color='skyblue')
plt.title('Витрати по точках доставки')
plt.ylabel('Гривні')
print("📊 Графік побудовано. Закрий його, щоб продовжити...")
plt.show()

# --- 4. КАРТА (Візуалізація) ---
# Створюємо просту карту (для прикладу координати центру Києва)
m = folium.Map(location=[50.45, 30.52], zoom_start=10)
folium.Marker([50.45, 30.52], popup="Склад").add_to(m)
m.save("map.html")
print("🗺️ Карта збережена у файл map.html. Відкрий його в браузері!")