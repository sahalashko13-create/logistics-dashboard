import streamlit as st
import pandas as pd

st.title("🚛 Перевірка зв'язку")
st.write("Якщо ви бачите цей текст, значить сайт працює!")

try:
    df = pd.read_csv('data.csv')
    st.success("Файл data.csv знайдено!")
    st.write(df.head())
except Exception as e:
    st.error(f"Помилка з файлом: {e}")
