import pandas as pd
from collections import defaultdict
import csv
import json
from datetime import datetime

def load_categories(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def load_repos(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def days_from_today(date):
    today = datetime.now().date()
    return (today - date.date()).days

def create_project_overview_report(csv_file, cat_file, repos_file, output_file='project_overview.md'):
    # Read the CSV file
    df = pd.read_csv(csv_file, sep='|', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

    # Load categories and repos data
    categories = load_categories(cat_file)
    repos_data = load_repos(repos_file)

    # Convert dates to datetime
    df['date_start'] = pd.to_datetime(df['date_start'])
    df['date_end'] = pd.to_datetime(df['date_end'])

    # Group by project
    project_data = defaultdict(lambda: {
        'start_date': None, 
        'end_date': None, 
        'categories': defaultdict(lambda: {'count': 0, 'libraries': set()}),
        'about': '',
        'overview': ''
    })

    for _, row in df.iterrows():
        project = row['project']
        library = row['library']
        
        if pd.notna(library):
            library = str(library)
            category = categories.get(library, 'Others')
            project_data[project]['categories'][category]['count'] += 1
            project_data[project]['categories'][category]['libraries'].add(library)
        
        if project_data[project]['start_date'] is None or row['date_start'] < project_data[project]['start_date']:
            project_data[project]['start_date'] = row['date_start']
        
        if project_data[project]['end_date'] is None or row['date_end'] > project_data[project]['end_date']:
            project_data[project]['end_date'] = row['date_end']
        
        if 'about' in row and pd.notna(row['about']):
            project_data[project]['about'] = row['about']

    # Add overview from repos.json
    for project, data in project_data.items():
        if project in repos_data:
            data['overview'] = repos_data[project].get('overview', '')

    # Sort projects by start date (descending)
    sorted_projects = sorted(project_data.items(), key=lambda x: x[1]['start_date'], reverse=True)

    # Generate the markdown report
    with open(output_file, 'w') as f:
        f.write("# Project Overview Report\n\n")
        
        for project, data in sorted_projects:
            f.write(f"## {project}\n\n")
            start_days = days_from_today(data['start_date'])
            end_days = days_from_today(data['end_date'])
            f.write(f"- **Start Date:** {data['start_date'].strftime('%Y-%m-%d')} ({start_days} days ago)\n")
            f.write(f"- **End Date:** {data['end_date'].strftime('%Y-%m-%d')} ({end_days} days ago)\n\n")
            
            if data['about']:
                f.write(f"**About:** {data['about']}\n\n")
            
            if data['overview']:
                f.write(f"**Overview:** {data['overview']}\n\n")
            
            f.write("- **Categories and Libraries Used:**\n")
            
            total_libraries = sum(cat_data['count'] for cat_data in data['categories'].values())
            sorted_categories = sorted(data['categories'].items(), key=lambda x: x[1]['count'], reverse=True)
            
            for category, cat_data in sorted_categories:
                percentage = (cat_data['count'] / total_libraries) * 100
                libraries_list = ", ".join(sorted(cat_data['libraries']))
                f.write(f"  - [{percentage:.0f}%] {category} [{libraries_list}]\n")
            
            f.write("\n")

    print(f"Project overview report saved as {output_file}")

if __name__ == "__main__":
    create_project_overview_report('git.csv', 'cat.json', 'repos.json')