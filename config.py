import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WATSON_API_KEY = os.getenv('WATSON_API_KEY', '7OEn5GkcdE2865B92U07vGg7fgtZ4f9wp0ivDpuWvGA0')
    WATSON_URL = os.getenv('WATSON_URL', 'https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/7c16e4d1-82e6-4b02-8fb3-cefc6fd6664e    ')
