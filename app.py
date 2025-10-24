from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 載入 routes
from routes.citation import bp as citation_bp
app.register_blueprint(citation_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
