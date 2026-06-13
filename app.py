from flask import Flask
import os
import socket

app = Flask(__name__)

@app.route('/')
def hello():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>John Bryce DevOps Project</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }}
            .container {{ background: white; padding: 30px; display: inline-block; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            p {{ color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>DevOps GitOps Pipeline Successful!</h1>
            <p><strong>Host Pod Name:</strong> {socket.gethostname()}</p>
            <p><strong>App Version:</strong> 1.0.0</p>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    # The application runs on port 8080 as specified in your architecture
    app.run(host="0.0.0.0", port=8080)