from dotenv import load_dotenv
import os

load_dotenv()

print('special value: ', os.getenv('special'))