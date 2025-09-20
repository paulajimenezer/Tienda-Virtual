from database.database import check_connection

if check_connection():
    print("✅ Conexión a Neon exitosa")
else:
    print("❌ Error de conexión")
