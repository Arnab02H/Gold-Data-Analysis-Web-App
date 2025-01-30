import pandas as pd
import plotly.express as px
from flask import Flask, render_template
import plotly.graph_objs as go
from plotly.subplots import make_subplots 
app = Flask(__name__)

# Read the data
df = pd.read_csv("Gold_Cleaned_Dataset.csv")

# Convert 'Dates' to date format
df['Dates'] = pd.to_datetime(df['Dates'], format='%Y-%m-%d')

# Adding a 'Year-Month' column for time-based analysis
df['Year_month'] = df['Dates'].dt.strftime('%Y-%m')

# Adding a 'Year' column for yearly analysis
df['Year'] = df['Dates'].dt.year
df['Month'] = df['Dates'].dt.month


# Summing occurrences of price directions
price_direction_counts = df[['Price Direction Up', 'Price Direction Constant', 'Price Direction Down']].sum()

# Create a DataFrame for plotting
price_direction_df = pd.DataFrame({
    'Direction': ['Up', 'Constant', 'Down'],
    'Frequency': price_direction_counts.values
})

# Count the sentiment distribution
sentiment_counts = df['Price Sentiment'].value_counts()

# Convert the sentiment counts to a DataFrame for plotting
sentiment_df = sentiment_counts.reset_index()
sentiment_df.columns = ['Sentiment', 'Frequency']

@app.route('/')
def home():
    return render_template('sidebar.html')

@app.route('/price_direction_analysis')
def price_direction_analysis():
    # Create the Plotly figure for Price Direction Analysis
    fig = px.bar(price_direction_df, x='Direction', y='Frequency', title='Gold Price Movement Distribution',
                 labels={'Direction': 'Price Direction', 'Frequency': 'Frequency'})
    
    # Embed the plot into HTML
    graph_html = fig.to_html(full_html=False)
    return render_template('graph.html', graph_html=graph_html)

@app.route('/sentiment_analysis')
def sentiment_analysis():
    # Create the Plotly figure for Sentiment Analysis with different shades of blue
    fig = px.pie(sentiment_df, names='Sentiment', values='Frequency', 
                 title='Sentiment Distribution',
                 color_discrete_sequence=px.colors.sequential.Blues)  # Different blue shades
    
    # Adjust the layout for a smaller pie chart size
    fig.update_layout(
        width=500,  # Set pie chart width
        height=400,  # Set pie chart height
        title_font_size=24,
        margin=dict(l=40, r=40, t=40, b=40)  # Adjust margins to make the graph smaller
    )
    
    # Embed the plot into HTML
    sentiment_graph_html = fig.to_html(full_html=False)
    
    # Return the graph to the 'graph2.html' template
    return render_template('graph2.html', sentiment_graph_html=sentiment_graph_html)

@app.route('/sentiment_impact')
def sentiment_impact():
    # Group by Price Sentiment and calculate sums for each Price Direction
    sentiment_impact = df.groupby('Price Sentiment').agg(
        Price_Direction_Up=('Price Direction Up', 'sum'),
        Price_Direction_Constant=('Price Direction Constant', 'sum'),
        Price_Direction_Down=('Price Direction Down', 'sum')
    ).reset_index()

    # Convert to long format for plotting
    sentiment_impact_long = sentiment_impact.melt(id_vars=['Price Sentiment'], 
                                                  value_vars=['Price_Direction_Up', 'Price_Direction_Constant', 'Price_Direction_Down'],
                                                  var_name='Price_Direction', 
                                                  value_name='Frequency')

    # Plot using Plotly Express
    fig = px.bar(sentiment_impact_long, 
                 x='Price Sentiment', 
                 y='Frequency', 
                 color='Price_Direction', 
                 barmode='group',
                 color_discrete_map={
                     'Price_Direction_Up': '#B0C4DE',
                     'Price_Direction_Constant': '#AFEEEE',
                     'Price_Direction_Down': '#87CEFA'
                 },
                 title='Sentiment Impact on Price Directions',
                 labels={'Price Sentiment': 'Price Sentiment', 'Frequency': 'Frequency'})

    fig.update_layout(xaxis_title='Price Sentiment', yaxis_title='Frequency', template='plotly_white')

    # Convert the plot to HTML and render in the template
    graph_html = fig.to_html(full_html=False)
    return render_template('graph3.html', graph_html=graph_html)


### month and year
@app.route('/month_and_year_analysis')
def month_and_year_analysis():
    # Make sure the Date column is in datetime format if not already
    df['Dates'] = pd.to_datetime(df['Dates'])

    # Add 'Year' and 'Month' columns for grouping
    df['Year'] = df['Dates'].dt.year
    df['Month'] = df['Dates'].dt.month

    # Yearly Trends Processing: Group by 'Year' and sum only numeric columns
    yearly_trends = df.groupby('Year')[['Price Direction Up', 'Price Direction Constant', 'Price Direction Down']].sum().reset_index()

    # Reshape the data for easier plotting (Yearly)
    yearly_trends_long = pd.melt(yearly_trends, id_vars='Year', 
                                 value_vars=['Price Direction Up', 'Price Direction Constant', 'Price Direction Down'],
                                 var_name='Price_Direction', value_name='Frequency')

    # Monthly Trends Processing: Group by 'Month' and sum only numeric columns
    monthly_trends = df.groupby('Month')[['Price Direction Up', 'Price Direction Constant', 'Price Direction Down']].sum().reset_index()

    # Reshape the data for easier plotting (Monthly)
    monthly_trends_long = pd.melt(monthly_trends, id_vars='Month', 
                                  value_vars=['Price Direction Up', 'Price Direction Constant', 'Price Direction Down'],
                                  var_name='Price_Direction', value_name='Frequency')

    # Create a combined figure using Plotly subplots
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Yearly Price Movement Trends', 'Monthly Price Movement Trends'))

    # Yearly Plot
    for direction in yearly_trends_long['Price_Direction'].unique():
        fig.add_trace(
            go.Bar(x=yearly_trends_long[yearly_trends_long['Price_Direction'] == direction]['Year'],
                   y=yearly_trends_long[yearly_trends_long['Price_Direction'] == direction]['Frequency'],
                   name=direction),
            row=1, col=1
        )

    # Monthly Plot
    for direction in monthly_trends_long['Price_Direction'].unique():
        fig.add_trace(
            go.Bar(x=monthly_trends_long[monthly_trends_long['Price_Direction'] == direction]['Month'],
                   y=monthly_trends_long[monthly_trends_long['Price_Direction'] == direction]['Frequency'],
                   name=direction),
            row=1, col=2
        )

    # Update layout for the combined plot
    fig.update_layout(title_text="Yearly and Monthly Price Movement Trends", 
                      barmode='group', 
                      showlegend=True, 
                      height=600)

    # Convert Plotly graph to HTML
    graph_html = fig.to_html(full_html=False)

    return render_template('graph4.html', graph_html=graph_html)
if __name__ == '__main__':
    app.run(debug=True)
