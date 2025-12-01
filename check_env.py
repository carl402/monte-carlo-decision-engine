import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Verificando variables de entorno...")
print(f"NEON_DATABASE_URL: {'✅ Configurada' if os.getenv('NEON_DATABASE_URL') else '❌ No encontrada'}")
print(f"PORT: {os.getenv('PORT', '8050')}")

if os.getenv('NEON_DATABASE_URL'):
    url = os.getenv('NEON_DATABASE_URL')
    print(f"URL: {url[:50]}...")
else:
    print("💡 Configura NEON_DATABASE_URL en Railway Settings → Variables")