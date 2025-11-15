from app import create_app, DB
from app import models
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, DB)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004,
        debug=True)
