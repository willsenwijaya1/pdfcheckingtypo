#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pdfplumber
import re
import time
from spellchecker import SpellChecker
import os

# Fungsi untuk mengambil teks dari PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ''
        for page in pdf.pages:
            full_text += page.extract_text()
    return full_text

# Fungsi untuk menghitung Levenshtein Distance
def dld(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    if lenstr1 == 0:
        return lenstr2
    if lenstr2 == 0:
        return lenstr1
    for i in range(-1, lenstr1):
        d[(i, -1)] = i + 1
    for j in range(-1, lenstr2):
        d[(-1, j)] = j + 1
    
    for i in range(lenstr1):
        for j in range(lenstr2):
            cost = 1
            if s1[i] == s2[j]:
                cost = 0
                
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,  # deletion
                d[(i, j - 1)] + 1,  # insertion
                d[(i - 1, j - 1)] + cost)  # substitution
    return d[lenstr1 - 1, lenstr2 - 1]

# Fungsi untuk membersihkan teks
def tokenize(text):
    result = text.lower()  # lowercase the text
    result = re.sub(r'[^a-z0-9 -]', ' ', result, flags=re.IGNORECASE | re.MULTILINE)
    result = re.sub(r'( +)', ' ', result, flags=re.IGNORECASE | re.MULTILINE)
    return result.strip()

# Streamlit app
st.title('Spell Checker for PDF')

# Form untuk mengunggah file PDF
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    # Simpan file yang diunggah
    with open("uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Ekstrak teks dari file PDF yang diunggah
    text = extract_text_from_pdf("uploaded_file.pdf")
    
    # Menampilkan teks yang diekstrak (opsional)
    st.subheader('Extracted Text from PDF:')
    st.text_area("Text from PDF", text, height=300)

    # Kamus pengecekan typo
    kamus = []
    with open("kamus.txt", 'r') as f:
        kamusmasuk = f.read()
        kamus = kamusmasuk.split('\n')

    # Cek typo
    words = text.split(' ')
    start = time.time()
    kalimatakhir = {}
    for x in words:
        z = tokenize(x)
        if z in kamus:
            kata = x
        else:
            kata = "*" + x
        kalimatakhir[kata] = 1

    hasilakhir = {}
    sarankata = {}
    for z in words:
        x = tokenize(z)
        if x not in kamus:
            salah = x
            hasilakhir = {y for y in kamus if [dld(x, y), y][0] == 1}
            if len(hasilakhir) != 0:
                sarankata[x] = hasilakhir
            else:
                sarankata[x] = "-"
    
    end = time.time()
    # Menampilkan waktu pemrosesan
    st.subheader(f"Processing Time: {end - start:.2f} seconds")
    
    # Menampilkan hasil pengecekan typo
    st.subheader('Suggested Corrections:')
    if sarankata:
        for word, suggestions in sarankata.items():
            st.write(f"Word: **{word}**")
            if suggestions != "-":
                st.write(f"Suggested Corrections: {', '.join(suggestions)}")
            else:
                st.write("No suggestions found")
    else:
        st.write("No typos found!")

