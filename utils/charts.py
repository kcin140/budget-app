import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def progress_bar(planned, spent):
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
