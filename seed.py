"""
Script para poblar la base de datos con datos iniciales.
"""

import uuid
from sqlalchemy.orm import sessionmaker
from database.config import engine
from Entities.usuarios import Usuarios
from Entities.roles import Roles
from Entities.sexo import Sexo
from Entities.tipo_documento import Tipo_documento
from Entities.categorias import Categorias
from Entities.productos import Productos

Session = sessionmaker(bind=engine)
session = Session()

rol_admin = Roles(id=uuid.uuid4(), nombre="admin")
session.add(rol_admin)

sexos = [
    Sexo(id=uuid.uuid4(), nombre="M"),
    Sexo(id=uuid.uuid4(), nombre="F"),
    Sexo(id=uuid.uuid4(), nombre="O"),
]
session.add_all(sexos)

tipos_doc = [
    Tipo_documento(id=uuid.uuid4(), nombre="CC"),
    Tipo_documento(id=uuid.uuid4(), nombre="TI"),
    Tipo_documento(id=uuid.uuid4(), nombre="PP"),
]
session.add_all(tipos_doc)

usuario_admin = Usuarios(
    id=uuid.uuid4(),
    nombre="Admin",
    apellido="Principal",
    email="admin@admin.com",
    password="admin123",  
    id_sexo=sexos[0].id,
    id_tipo_documento=tipos_doc[0].id,
    numero_documento="123456789",
    id_rol=rol_admin.id,
    activo=True,
    id_usuario_crea=None,  
    id_usuario_edita=None,
)
session.add(usuario_admin)

cat1 = Categorias(id=uuid.uuid4(), nombre="Electrónica")
cat2 = Categorias(id=uuid.uuid4(), nombre="Ropa")
session.add_all([cat1, cat2])

prod1 = Productos(id=uuid.uuid4(), nombre="Laptop", id_categoria=cat1.id, precio=1000)
prod2 = Productos(id=uuid.uuid4(), nombre="Camiseta", id_categoria=cat2.id, precio=20)
session.add_all([prod1, prod2])

session.commit()
session.close()
print("Datos iniciales insertados correctamente.")