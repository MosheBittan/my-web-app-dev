from flask import Flask
import plotly.graph_objs as go
import plotly.io as pio
import random
import socket
import os

app = Flask(__name__)

def get_k8s_metadata():
    """Extracts Kubernetes metadata natively from the container environment."""
    # In Kubernetes, the container's hostname is always the Pod's name
    pod_name = socket.gethostname()
    
    try:
        pod_ip = socket.gethostbyname(pod_name)
    except Exception:
        pod_ip = "Unknown"

    # K8s pod names follow the format: [deployment-name]-[replicaset-hash]-[pod-hash]
    parts = pod_name.split('-')
    if len(parts) >= 3:
        pod_hash = parts[-1]
        rs_hash = parts[-2]
        deployment = "-".join(parts[:-2])
    else:
        pod_hash = "N/A"
        rs_hash = "N/A"
        deployment = "Standalone Pod"

    return {
        "Deployment Name": deployment,
        "Pod Name": pod_name,
        "Replica ID (Hash)": pod_hash,
        "ReplicaSet": rs_hash,
        "Internal Pod IP": pod_ip,
        "Python Version": os.environ.get("PYTHON_VERSION", "3.9")
    }

@app.route('/')
def index():
    # 1. Fetch Kubernetes Metadata
    k8s_data = get_k8s_metadata()

    # 2. Generate Mock Data for the Graph
    hours = list(range(24))
    cpu_usage = [random.uniform(20, 85) for _ in hours]
    memory_usage = [random.uniform(40, 75) for _ in hours]

    # 3. Build the Interactive Graph using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=cpu_usage, mode='lines+markers', name='CPU Load (%)', line=dict(color='#00ffcc', width=3)))
    fig.add_trace(go.Scatter(x=hours, y=memory_usage, mode='lines+markers', name='Memory Usage (%)', line=dict(color='#ff007f', width=3)))

    fig.update_layout(
        title="Live Container Resource Utilization",
        xaxis_title="Hour of Day",
        yaxis_title="Usage (%)",
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    graph_html = pio.to_html(fig, full_html=False)

    # 4. Generate the HTML for the Metadata Table
    meta_html = ""
    for key, value in k8s_data.items():
        meta_html += f"<tr><td class='meta-key'>{key}</td><td class='meta-val'>{value}</td></tr>"

    # 5. Build the Webpage Interface
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Moshe's Cloud-Native Dashboard</title>
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
            h1 {{ color: #00ffcc; margin-bottom: 5px; }}
            p.subtitle {{ color: #aaaaaa; margin-bottom: 30px; }}
            
            /* K8s Metadata Table Styles */
            .meta-table {{
                width: 100%;
                max-width: 600px;
                margin: 0 auto 30px auto;
                border-collapse: collapse;
                background-color: #2a2a2a;
                border-radius: 8px;
                overflow: hidden;
            }}
            .meta-table td {{
                padding: 12px 15px;
                border-bottom: 1px solid #3a3a3a;
                text-align: left;
            }}
            .meta-table tr:last-child td {{ border-bottom: none; }}
            .meta-key {{ font-weight: bold; color: #ff007f; width: 40%; }}
            .meta-val {{ color: #e0e0e0; font-family: monospace; font-size: 1.1em; }}
        </style>
    </head>
    <body>
        <div class="dashboard-container">
            <h1>🚀 Moshe's Cloud-Native Telemetry</h1>
            <p class="subtitle">Deployed via Jenkins CI/CD & ArgoCD GitOps</p>
            
            <table class="meta-table">
                <tbody>
                    {meta_html}
                </tbody>
            </table>
            
            {graph_html}
            
        </div>
    </body>
    </html>
    """
    
    return html_template

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)