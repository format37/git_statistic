import pandas as pd
from collections import defaultdict
import csv
import json

def load_categories(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def create_project_overview_report(csv_file, cat_file, output_file='project_overview.md'):
    # Read the CSV file
    df = pd.read_csv(csv_file, sep='|', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

    # Load categories
    categories = load_categories(cat_file)

    # Convert dates to datetime
    df['date_start'] = pd.to_datetime(df['date_start'])
    df['date_end'] = pd.to_datetime(df['date_end'])

    # Group by project
    project_data = defaultdict(lambda: {
        'start_date': None, 
        'end_date': None, 
        'categories': defaultdict(lambda: {'count': 0, 'libraries': set()}),
        'about': ''
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

    # Sort projects by start date (descending)
    sorted_projects = sorted(project_data.items(), key=lambda x: x[1]['start_date'], reverse=True)

    # Generate the markdown report
    with open(output_file, 'w') as f:
        f.write("# Project Overview Report\n\n")
        
        for project, data in sorted_projects:
            f.write(f"## {project}\n\n")
            f.write(f"- **Start Date:** {data['start_date'].strftime('%Y-%m-%d')}\n")
            f.write(f"- **End Date:** {data['end_date'].strftime('%Y-%m-%d')}\n")
            f.write("- **Categories and Libraries Used:**\n")
            
            total_libraries = sum(cat_data['count'] for cat_data in data['categories'].values())
            sorted_categories = sorted(data['categories'].items(), key=lambda x: x[1]['count'], reverse=True)
            
            for category, cat_data in sorted_categories:
                percentage = (cat_data['count'] / total_libraries) * 100
                libraries_list = ", ".join(sorted(cat_data['libraries']))
                f.write(f"  - [{percentage:.0f}%] {category} [{libraries_list}]\n")
            
            if data['about']:
                f.write(f"\n**About:** {data['about']}\n")
            f.write("\n")

    print(f"Project overview report saved as {output_file}")

if __name__ == "__main__":
    create_project_overview_report('git.csv', 'cat.json')