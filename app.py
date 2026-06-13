from flask import Flask
import plotly.graph_objs as go
import plotly.io as pio
import random

app = Flask(__name__)

@app.route('/')
def index():
    # 1. Generate Mock Data (Simulating 24 hours of server metrics)
    hours = list(range(24))
    cpu_usage = [random.uniform(20, 85) for _ in hours]
    memory_usage = [random.uniform(40, 75) for _ in hours]

    # 2. Build the Interactive Graph using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=cpu_usage, mode='lines+markers', name='CPU Load (%)', line=dict(color='#00ffcc', width=3)))
    fig.add_trace(go.Scatter(x=hours, y=memory_usage, mode='lines+markers', name='Memory Usage (%)', line=dict(color='#ff007f', width=3)))

    # 3. Style the Graph (Dark Mode)
    fig.update_layout(
        title="Live Cluster Resource Utilization",
        xaxis_title="Hour of Day",
        yaxis_title="Usage (%)",
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=60, b=40)
    )

    # Convert the graph to HTML format so Flask can render it
    graph_html = pio.to_html(fig, full_html=False)

    # 4. Build the Webpage Interface
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Moshe's DevOps Dashboard</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #121212;
                color: #ffffff;
                text-align: center;
                margin: 0;
                padding: 40px;
            }}
            .dashboard-container {{
                max-width: 1000px;
                margin: 0 auto;
                background-color: #1e1e1e;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.8);
            }}
            h1 {{
                color: #00ffcc;
                margin-bottom: 5px;
            }}
            p.subtitle {{
                color: #aaaaaa;
                margin-bottom: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="dashboard-container">
            <h1>🚀 Application Telemetry</h1>
            <p class="subtitle">Deployed via Jenkins CI/CD & ArgoCD GitOps</p>
            
            {graph_html}
            
        </div>
    </body>
    </html>
    """
    
    return html_template

if __name__ == '__main__':
    # Ensure this matches the port exposed in your Dockerfile (typically 8080 or 5000)
    app.run(host='0.0.0.0', port=8090)