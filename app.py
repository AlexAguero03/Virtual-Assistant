from app import create_app
from app.utils import cargar_modelo



app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
