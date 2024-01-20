import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class LibraryUsagePlot:
    def __init__(self, category_file, git_file, enabled_categories_file):
        self.category_file = category_file
        self.git_file = git_file
        self.enabled_categories_file = enabled_categories_file

    def categorize_library(self, library, categories):
        """
        Categorize a library, assigning 'Other' to libraries with empty categories.

        Parameters:
        library (str): The name of the library.
        categories (dict): A dictionary of categories keyed by library names.

        Returns:
        str: The category name, or 'Other' for libraries not found in categories or with empty category names.
        """
        return categories.get(library, 'Other') if categories.get(library, 'Other') != '' else 'Other'

    def generate_filename(self, enabled_categories):
        """
        Generates a filename based on the first few characters of enabled category names.

        Parameters:
        enabled_categories (list): List of enabled category names.

        Returns:
        str: A filename constructed from the unique abbreviations of the category names.
        """
        i = 1
        while True:
            # Create abbreviations by slicing the first i characters of each category
            abbreviations = [cat[:i].replace(' ','_') for cat in enabled_categories]
    
            # Check if all abbreviations are unique
            if len(set(abbreviations)) == len(enabled_categories):
                # Join the abbreviations with an underscore and add the prefix 'report_'
                filename = 'report_' + '-'.join(abbreviations) + '.html'
                return filename
    
            i += 1  # Increase the number of characters to take from each category

    def load_categories(self):
        """
        Load the categories from the category file.

        Returns:
        dict: The categories dictionary.
        """
        categories_df = pd.read_json(self.category_file, orient='index')
        categories_dict = categories_df.to_dict()[0]
        return categories_dict

    def load_enabled_categories(self):
        """
        Load the enabled categories from the enabled categories file.

        Returns:
        list: The list of enabled categories.
        """
        enabled_categories = []
        with open(self.enabled_categories_file, 'r') as file:
            for line in file:
                enabled_categories.append(line.strip())
        return enabled_categories
    
    def print_categories(self):
        """
        Print the categories and enabled categories.
        """
        categories = self.load_categories()
        enabled_categories = self.load_enabled_categories()

        all_categories = [category if category != '' else 'Other' for category in categories.values()]

        print('\n# All categories:')
        for category in sorted(set(all_categories)):
            print(category)

        print('\n# Enabled categories:')
        for category in sorted(enabled_categories):
            print(category)

    def plot_library_usage_by_category(self):
        """
        Creates an interactive plot of library usage over time, colored by category.
        Each category can be toggled on or off in the plot. Certain categories are disabled (visible in legend only) by default.
        """
        # Load the Git dataset
        df = pd.read_csv(self.git_file)

        # Load categories
        categories = self.load_categories()

        # Apply the categorization function to the 'library' column
        df['category'] = df['library'].apply(self.categorize_library, args=(categories,))

        # Sort the DataFrame by 'date_end' in descending order
        df_sorted = df.sort_values(by='date_end', ascending=False)

        # Load enabled categories
        enabled_categories = self.load_enabled_categories()

        # Get unique categories and assign colors
        all_categories = df_sorted['category'].unique()
        colors = px.colors.qualitative.Plotly

        # Create a Plotly figure
        fig = go.Figure()

        # Create a dictionary to map categories to traces
        category_to_trace = {}

        # Add a single trace for each category with both start and end dates
        for i, category in enumerate(all_categories):
            category_df = df_sorted[df_sorted['category'] == category]

            # Check if the category is enabled (visible in the plot)
            visible = True if category in enabled_categories else 'legendonly'

            # Combine start and end dates
            trace = go.Scatter(
                x=category_df['date_start'].tolist() + category_df['date_end'].tolist(),
                y=category_df['library'].tolist() + category_df['library'].tolist(),
                mode='markers',
                name=category,
                visible=visible,
                marker=dict(color=colors[i % len(colors)],
                            symbol=['circle'] * len(category_df) + ['x'] * len(category_df)),
            )

            # Store the trace in the category_to_trace mapping
            category_to_trace[category] = trace

        # Sort the categories for legend, moving enabled categories to the top
        legend_order = sorted(all_categories, key=lambda c: (0, c) if c in enabled_categories else (1, c))

        # Add the traces to the figure in the desired legend order
        for category in legend_order:
            trace = category_to_trace[category]
            fig.add_trace(trace)

        # Update layout
        fig.update_layout(
            title='Usage of Libraries Over Time by Category',
            xaxis_title='Date',
            yaxis_title='Libraries',
            legend_title='Categories',
            template="plotly_white"
        )

        # Generate filename
        filename = self.generate_filename(enabled_categories)

        # Save the plot as an HTML file
        fig.write_html(filename)

        # Show the plot
        fig.show()

def main():
    plot = LibraryUsagePlot('cat.json', 'git.csv', 'enabled_categories.txt')
    plot.print_categories()
    plot.plot_library_usage_by_category()

if __name__ == '__main__':
    main()