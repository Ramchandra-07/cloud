import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import docx2txt
import PyPDF2
import re
import numpy as np
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)




#new functionalities:
# Add a function to check if the user is authenticated
def user_authenticated():
    return 'username' in session

# Function to check if user is logged in
def user_logged_in():
    return 'user_id' in session

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def user_exists(username):
    conn = sqlite3.connect('unique_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    result = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return result

def add_user(username, password):
    conn = sqlite3.connect('unique_database.db')
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    cursor.close()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('unique_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    if user and check_password_hash(user[2], password):
        session['user_id'] = user[0]
        result = True
    else:
        result = False
    cursor.close()
    conn.close()
    return result

def get_user_id(username):
    conn = sqlite3.connect('unique_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return result

