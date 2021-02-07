import os

DATABASE_FILE_PATH = os.path.join(os.getcwd(), 'sqlite.db')
DATABASE_CONNECTION_PATH = 'sqlite:///' + DATABASE_FILE_PATH
