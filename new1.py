#after adding search button

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import docx2txt
import PyPDF2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'doc', 'docx'}

# Function to check if the filename has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Placeholder function to extract text from a resume
def extract_text_from_resume(resume_filepath):
    # Check the file extension
    _, file_extension = os.path.splitext(resume_filepath)
    
    # Extract text based on the file extension
    if file_extension.lower() == '.txt':
        with open(resume_filepath, 'r', encoding='utf-8') as file:
            text = file.read()
    elif file_extension.lower() == '.pdf':
        text = ''
        def extract_text_from_resume(resume_filepath):
            with open(resume_filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                for page_number in range(num_pages):
                    page = pdf_reader.pages[page_number]
                    text += page.extract_text()
            return text
    elif file_extension.lower() == '.docx':
        text = docx2txt.process(resume_filepath)
    else:
        # Unsupported file format
        text = None
    
    return text

# Connect to the SQLite database
conn = sqlite3.connect('unique_database.db')

# Read data from the 'jobs' table into a pandas DataFrame
jobs_data = pd.read_sql_query("SELECT * FROM unique_jobs", conn)

# Preprocessing the job descriptions
tfidf_vectorizer = TfidfVectorizer(stop_words='english')

# Concatenate job text for TF-IDF vectorization
job_text = jobs_data['Job Title'] + ' ' + jobs_data['skills'] + ' ' + jobs_data['Role'] + ' ' + jobs_data['Responsibilities']

# Fit and transform TF-IDF vectors for job text
job_tfidf_matrix = tfidf_vectorizer.fit_transform(job_text)
# Function to recommend jobs based on a given resume
def recommend_jobs(resume_text, num_recommendations=5):
    # Calculate TF-IDF vectors for the resume and job descriptions
    resume_vector = tfidf_vectorizer.transform([resume_text])
    job_desc_vectors = tfidf_vectorizer.transform(jobs_data['Job Description'])

    # Calculate cosine similarity based on job descriptions
    cosine_similarities_desc = cosine_similarity(resume_vector, job_desc_vectors).flatten()

    # Calculate TF-IDF vectors for other relevant features
    features_to_consider = ['Experience', 'Job Title', 'Role', 'skills', 'Responsibilities']
    job_feature_vectors = tfidf_vectorizer.transform(jobs_data[features_to_consider].fillna('').apply(lambda x: ' '.join(x), axis=1))

    # Calculate cosine similarity based on other features
    cosine_similarities_features = cosine_similarity(resume_vector, job_feature_vectors).flatten()

    # Combine the similarity scores from both descriptions and other features
    combined_similarities = 0.6 * cosine_similarities_desc + 0.4 * cosine_similarities_features

    # Get indices of top recommended jobs based on combined similarity scores
    top_indices = combined_similarities.argsort()[-num_recommendations:][::-1]

    # Get the recommended job listings
    recommended_jobs = jobs_data.iloc[top_indices]

    # Calculate the matching percentage based on combined similarity scores
    recommended_jobs['Matching_Percentage'] = combined_similarities[top_indices] * 100

    return recommended_jobs

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        resume_text = extract_text_from_resume(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Placeholder function
        recommended_jobs = recommend_jobs(resume_text)
        return render_template('job_listings.html', job_listings=recommended_jobs.to_dict(orient='records'))
    return redirect(request.url)


@app.route('/search', methods=['GET', 'POST'])
def search_jobs():
    query = request.args.get('query')
    if query:
        print("Received search query:", query)  # Debug statement
        
        # Transform the query into a TF-IDF vector
        query_vector = tfidf_vectorizer.transform([query])

        # Calculate cosine similarity between the query vector and job TF-IDF matrix
        cosine_similarities = cosine_similarity(query_vector, job_tfidf_matrix).flatten()

        # Get indices of jobs with high similarity
        top_indices = cosine_similarities.argsort()[::-1]

        # Filter jobs based on cosine similarity threshold
        threshold = 0.2  # Adjust as needed
        filtered_jobs = jobs_data.iloc[top_indices][cosine_similarities[top_indices] > threshold]

        print("Number of filtered jobs:", len(filtered_jobs))  # Debug statement

        # Render the job listings template with filtered jobs
        return render_template('search_result.html', job_listings=filtered_jobs.to_dict(orient='records'))
    else:
        # If no query provided, render an empty job listings page
        return render_template('search_result.html', job_listings=[])


if __name__ == '__main__':
    app.run(debug=True)
