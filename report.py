import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def categorize_library(library, categories):
    # print(library, len(categories), categories[0])
    return categories.get(library, '')

def interactive_library_usage_by_category(df):
    """
    Creates an interactive plot of library usage over time, colored by category.
    Each category can be toggled on or off in the plot.

    Parameters:
    df (DataFrame): DataFrame containing the columns 'date', 'library', and 'category'.
    """

    # Get unique categories and assign colors
    categories = df['category'].unique()
    colors = px.colors.qualitative.Plotly

    # Create a Plotly figure
    fig = go.Figure()

    # Add a trace for each category
    for i, category in enumerate(categories):
        category_df = df[df['category'] == category]
        # Start Dates
        fig.add_trace(go.Scatter(
            x=category_df['date_start'],
            y=category_df['library'],
            mode='markers',
            name=f'{category} - Start',
            marker=dict(color=colors[i % len(colors)], symbol='circle'),
            legendgroup=category
        ))

        # End Dates
        fig.add_trace(go.Scatter(
            x=category_df['date_end'],
            y=category_df['library'],
            mode='markers',
            name=f'{category} - End',
            marker=dict(color=colors[i % len(colors)], symbol='x'),
            legendgroup=category
        ))

    # Update layout
    fig.update_layout(
        title='Usage of Libraries Over Time by Category',
        xaxis_title='Date',
        yaxis_title='Libraries',
        legend_title='Categories',
        template="plotly_white"
    )

    # Save the plot as an HTML file
    fig.write_html('report.html')

    # Show the plot
    fig.show()



def main():
    # Read categories
    cat = pd.read_json('cat.json', orient='index')
    # Convert cat to dict
    cat = cat.to_dict()[0]
    df = pd.read_csv('git.csv')
    # Apply the categorization function to the 'library' column
    df['category'] = df['library'].apply(categorize_library, args=(cat,))
    df_sorted = df.sort_values(by='date_end', ascending=False)

    interactive_library_usage_by_category(df_sorted)

if __name__ == '__main__':
    main()