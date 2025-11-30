import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def category_progress_chart(categories_data, category_spending):
    """
    Create a grouped bar chart showing planned vs actual for all categories
    """
    import plotly.graph_objects as go
    
    # Prepare data
    category_names = []
    planned_amounts = []
    actual_amounts = []
    
    for cat in categories_data:
        cat_name = cat['name']
        # Skip Mortgage to prevent scale skewing
        if cat_name == 'Mortgage':
            continue
            
        planned = float(cat['planned_amount'])
        actual = category_spending[category_spending['category'] == cat_name]['amount'].sum() if cat_name in category_spending['category'].values else 0
        
        category_names.append(cat_name)
        planned_amounts.append(planned)
        actual_amounts.append(actual)
    
    # Create grouped horizontal bar chart
    fig = go.Figure(data=[
        go.Bar(name='Planned', y=category_names, x=planned_amounts, marker_color='lightblue', orientation='h'),
        go.Bar(name='Actual', y=category_names, x=actual_amounts, marker_color='coral', orientation='h')
    ])
    
    fig.update_layout(
        barmode='group',
        title='Budget Progress by Category',
        yaxis_title='Category',
        xaxis_title='Amount ($)',
        height=max(400, len(category_names) * 30),  # Dynamic height based on number of categories
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def progress_bar(planned, spent):
    """Legacy function - kept for compatibility"""
    """
    Creates a horizontal bar chart showing progress towards the budget.
    Red if overspent, Green/Blue if within budget.
    """
    color = "green" if spent <= planned else "red"
    
    fig = go.Figure(go.Indicator(
        mode = "number+gauge+delta",
        value = spent,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Monthly Budget"},
        delta = {'reference': planned},
        gauge = {
            'shape': "bullet",
            'axis': {'range': [None, max(planned, spent) * 1.2]},
            'threshold': {
                'line': {'color': "red", 'width': 2},
                'thickness': 0.75,
                'value': planned
            },
            'bar': {'color': color}
        }
    ))
    fig.update_layout(height=250)
    return fig

def pie_chart(df):
    """
    Creates a pie chart of category spending.
    Expects df to have 'category' and 'amount' columns.
    """
    if df.empty:
        return go.Figure()
        
    fig = px.pie(df, values='amount', names='category', title='Spending by Category')
    return fig

def daily_spending(df):
    """
    Creates a line chart for daily cumulative spending for the current month.
    Expects df to have 'timestamp' and 'amount' columns.
    """
    if df.empty:
        return go.Figure()
    
    # Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Sort by date
    df = df.sort_values('timestamp')
    
    # Group by day and sum
    daily = df.groupby(df['timestamp'].dt.date)['amount'].sum().reset_index()
    daily['cumulative'] = daily['amount'].cumsum()
    
    fig = px.line(daily, x='timestamp', y='cumulative', title='Cumulative Daily Spending', markers=True)
    return fig
