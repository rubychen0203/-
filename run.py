from flask import Flask
from app import create_app  # 從 app 導入 db 和 create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
