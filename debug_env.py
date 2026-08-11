import os
from pathlib import Path
from dotenv import load_dotenv
p = Path(__file__).parent / '.env'
print('script path:', Path(__file__).resolve())
print('env path:', p.resolve())
print('exists:', p.exists())
load_dotenv(p)
print('API_Key:', os.getenv('API_Key'))
print('GEMINI_API_KEY:', os.getenv('GEMINI_API_KEY'))
