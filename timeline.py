import pandas as pd
import plotly.graph_objects as go
import csv

def create_project_timeline_plot(csv_file, output_file='project_timeline.html'):
    # Read the CSV file
    df = pd.read_csv(csv_file, sep='|', quoting=csv.QUOTE_MINIMAL, escapechar='\\')

    # Convert dates to datetime
    df['date_start'] = pd.to_datetime(df['date_start'])
    df['date_end'] = pd.to_datetime(df['date_end'])

    # Group by project and get the earliest start date and latest end date
    project_df = df.groupby('project').agg({
        'date_start': 'min',
        'date_end': 'max'
    }).reset_index()

    # Correct any mixed up dates
    project_df['date_start'], project_df['date_end'] = zip(*project_df.apply(lambda row: (min(row['date_start'], row['date_end']), max(row['date_start'], row['date_end'])), axis=1))

    # Calculate the overall start date (earliest of all projects)
    overall_start = project_df['date_start'].min()

    # Calculate start offset and duration for each project
    project_df['start_offset'] = (project_df['date_start'] - overall_start).dt.total_seconds() / (24 * 3600)
    project_df['duration'] = (project_df['date_end'] - project_df['date_start']).dt.total_seconds() / (24 * 3600)

    # Sort by start date
    project_df = project_df.sort_values('date_start')

    # Create the figure
    fig = go.Figure()

    # Generate a color for each project
    colors = [f'rgb({hash(project) % 256}, {(hash(project) >> 8) % 256}, {(hash(project) >> 16) % 256})' 
              for project in project_df['project']]

    # Add traces for each project
    for i, row in project_df.iterrows():
        fig.add_trace(
            go.Bar(
                x=[row['duration']],
                y=[row['project']],
                orientation='h',
                marker_color=colors[i],
                name=row['project'],
                hoverinfo='text',
                hovertext=f"{row['project']}<br>Start: {row['date_start'].date()}<br>End: {row['date_end'].date()}<br>Duration: {row['duration']:.1f} days",
                showlegend=False,
                base=row['start_offset']  # Set the start point of each bar
            )
        )

    # Update layout
    fig.update_layout(
        title='Project Timeline',
        height=max(600, len(project_df) * 30),  # Adjust height based on number of projects
        margin=dict(l=150, r=10, t=30, b=10),
        yaxis=dict(
            title='Projects',
            tickmode='array',
            tickvals=project_df['project'],
            ticktext=project_df['project'],
            automargin=True,
            tickfont=dict(size=10)
        ),
        xaxis=dict(
            title='Timeline (days since earliest project start)',
            showgrid=True,
            zeroline=True,
            zerolinecolor='rgba(0,0,0,0.5)',
            zerolinewidth=2,
        ),
        plot_bgcolor='rgba(0,0,0,0)',
    )

    # Add a vertical line at x=0 to represent the start of the timeline
    fig.add_shape(
        type="line",
        x0=0, y0=0, x1=0, y1=1,
        yref="paper",
        line=dict(color="rgba(0,0,0,0.5)", width=2)
    )

    # Save the plot as an HTML file
    fig.write_html(output_file, full_html=False, include_plotlyjs='cdn')

    print(f"Timeline plot saved as {output_file}")

if __name__ == "__main__":
    create_project_timeline_plot('git.csv')