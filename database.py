import pandas as pd
import sqlite3
import random

# Read the dataset into a pandas DataFrame
data = pd.read_csv('job_descriptions.csv')  # Replace 'your_dataset.csv' with the path to your dataset

# Select random 10,000 rows
data = data.sample(n=100000)

# Filter out rows with specified job titles
job_titles_to_include = [
    'Software Engineer', 'Data Scientist', 'IT Manager', 'Systems Administrator', 'Product Manager',
    'Network Engineer', 'Business Analyst', 'UX Designer', 'Database Administrator', 'Cybersecurity Analyst',
    'Project Manager', 'DevOps Engineer', 'Technical Support Specialist', 'Quality Assurance Engineer',
    'Cloud Architect', 'Machine Learning Engineer', 'Information Security Manager', 'Web Developer',
    'Software Developer', 'Data Analyst', 'Systems Analyst', 'Network Administrator', 'Product Owner',
    'Scrum Master', 'AI Engineer', 'Solutions Architect', 'IT Consultant', 'Database Developer', 'IT Director',
    'Technology Manager', 'Business Intelligence Analyst', 'Technical Writer', 'Infrastructure Engineer',
    'Enterprise Architect', 'IT Auditor', 'Data Engineer', 'Operations Manager', 'Release Manager',
    'Systems Integrator', 'IT Support Technician', 'Application Support Analyst', 'Technical Trainer',
    'Change Management Specialist', 'IT Procurement Manager', 'IT Risk Analyst', 'Compliance Officer'
]
data = data[data['Job Title'].isin(job_titles_to_include)]

# Establish a connection to the SQLite database
conn = sqlite3.connect('job_database.db')  # Create a new SQLite database or connect to an existing one
cursor = conn.cursor()

# Create a table in the database to store the data
cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
                    Job_Id TEXT PRIMARY KEY,
                    Experience TEXT,
                    Qualifications TEXT,
                    Salary_Range TEXT,
                    Location TEXT,
                    Country TEXT,
                    Work_Type TEXT,
                    Company_Size TEXT,
                    Preference TEXT,
                    Contact_Person TEXT,
                    Contact TEXT,
                    Job_Title TEXT,
                    Role TEXT,
                    Job_Portal TEXT,
                    Job_Description TEXT,
                    Benefits TEXT,
                    Skills TEXT,
                    Responsibilities TEXT,
                    Company_Name TEXT,
                    Company_Profile TEXT
                )''')

# Insert data into the table
data.to_sql('jobs', conn, if_exists='replace', index=False)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database created successfully.")
