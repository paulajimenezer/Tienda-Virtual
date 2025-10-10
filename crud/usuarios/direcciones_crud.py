"""
Operaciones CRUD para la entidad Direcciones de usuario usando SQLAlchemy.

Incluye creación, lectura, actualización, eliminación y utilidades de consulta con
validaciones de datos y verificación de referencias.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from Entities.direcciones import Direcciones as DIRECCIONES
from Entities.usuarios import Usuarios as USUARIOS

PAISES_VALIDOS = [
    "Afganistán",
    "Albania",
    "Alemania",
    "Andorra",
    "Angola",
    "Antigua y Barbuda",
    "Arabia Saudita",
    "Argelia",
    "Argentina",
    "Armenia",
    "Australia",
    "Austria",
    "Azerbaiyán",
    "Bahamas",
    "Bangladés",
    "Barbados",
    "Baréin",
    "Bélgica",
    "Belice",
    "Benín",
    "Bielorrusia",
    "Birmania",
    "Bolivia",
    "Bosnia y Herzegovina",
    "Botsuana",
    "Brasil",
    "Brunéi",
    "Bulgaria",
    "Burkina Faso",
    "Burundi",
    "Bután",
    "Cabo Verde",
    "Camboya",
    "Camerún",
    "Canadá",
    "Catar",
    "Chad",
    "Chile",
    "China",
    "Chipre",
    "Colombia",
    "Comoras",
    "Corea del Norte",
    "Corea del Sur",
    "Costa de Marfil",
    "Costa Rica",
    "Croacia",
    "Cuba",
    "Dinamarca",
    "Dominica",
    "Ecuador",
    "Egipto",
    "El Salvador",
    "Emiratos Árabes Unidos",
    "Eritrea",
    "Eslovaquia",
    "Eslovenia",
    "España",
    "Estados Unidos",
    "Estonia",
    "Esuatini",
    "Etiopía",
    "Filipinas",
    "Finlandia",
    "Fiyi",
    "Francia",
    "Gabón",
    "Gambia",
    "Georgia",
    "Ghana",
    "Granada",
    "Grecia",
    "Guatemala",
    "Guinea",
    "Guinea ecuatorial",
    "Guinea-Bisáu",
    "Guyana",
    "Haití",
    "Honduras",
    "Hungría",
    "India",
    "Indonesia",
    "Irak",
    "Irán",
    "Irlanda",
    "Islandia",
    "Islas Marshall",
    "Islas Salomón",
    "Israel",
    "Italia",
    "Jamaica",
    "Japón",
    "Jordania",
    "Kazajistán",
    "Kenia",
    "Kirguistán",
    "Kiribati",
    "Kuwait",
    "Laos",
    "Lesoto",
    "Letonia",
    "Líbano",
    "Liberia",
    "Libia",
    "Liechtenstein",
    "Lituania",
    "Luxemburgo",
    "Madagascar",
    "Malasia",
    "Malaui",
    "Maldivas",
    "Malí",
    "Malta",
    "Marruecos",
    "Mauricio",
    "Mauritania",
    "México",
    "Micronesia",
    "Moldavia",
    "Mónaco",
    "Mongolia",
    "Montenegro",
    "Mozambique",
    "Namibia",
    "Nauru",
    "Nepal",
    "Nicaragua",
    "Níger",
    "Nigeria",
    "Noruega",
    "Nueva Zelanda",
    "Omán",
    "Países Bajos",
    "Pakistán",
    "Palaos",
    "Palestina",
    "Panamá",
    "Papúa Nueva Guinea",
    "Paraguay",
    "Perú",
    "Polonia",
    "Portugal",
    "Reino Unido",
    "República Centroafricana",
    "República Checa",
    "República del Congo",
    "República Democrática del Congo",
    "República Dominicana",
    "Ruanda",
    "Rumanía",
    "Rusia",
    "Samoa",
    "San Cristóbal y Nieves",
    "San Marino",
    "San Vicente y las Granadinas",
    "Santa Lucía",
    "Santo Tomé y Príncipe",
    "Senegal",
    "Serbia",
    "Seychelles",
    "Sierra Leona",
    "Singapur",
    "Siria",
    "Somalia",
    "Sri Lanka",
    "Sudáfrica",
    "Sudán",
    "Sudán del Sur",
    "Suecia",
    "Suiza",
    "Surinam",
    "Tailandia",
    "Tanzania",
    "Tayikistán",
    "Timor Oriental",
    "Togo",
    "Tonga",
    "Trinidad y Tobago",
    "Túnez",
    "Turkmenistán",
    "Turquía",
    "Tuvalu",
    "Ucrania",
    "Uganda",
    "Uruguay",
    "Uzbekistán",
    "Vanuatu",
    "Vaticano",
    "Venezuela",
    "Vietnam",
    "Yemen",
    "Yibuti",
    "Zambia",
    "Zimbabue",
]


class DireccionCRUD:
    """
    Operaciones CRUD y utilidades de consulta para Direcciones de usuario.
    """

    def __init__(self, db: Session):
        """
        Inicializa el CRUD con una sesión de base de datos.

        Args:
            db: Sesión de SQLAlchemy.
        """
        self.db = db

    def crear_direccion(
        self,
        id_usuario: UUID,
        direccion: str,
        ciudad: str,
        departamento: str,
        pais: str,
        id_usuario_crea: Optional[UUID] = None,
    ) -> DIRECCIONES:
        """
        Crea una nueva dirección con validaciones y FK de usuario.

        Args:
            id_usuario: UUID del usuario propietario.
            direccion: Dirección principal (máximo 200 caracteres).
            ciudad: Ciudad (máximo 100 caracteres).
            departamento: Departamento/Estado (máximo 100 caracteres).
            pais: País (máximo 100 caracteres).
            id_usuario_crea: UUID del usuario que crea la dirección (opcional).

        Returns:
            Instancia creada de DIRECCIONES.

        Raises:
            ValueError: Si algún dato es inválido o el usuario no existe.
        """
        if not direccion or len(direccion.strip()) == 0:
            raise ValueError("La dirección es obligatoria")
        if len(direccion) > 200:
            raise ValueError("La dirección no puede exceder 200 caracteres")
        if not ciudad or len(ciudad.strip()) == 0:
            raise ValueError("La ciudad es obligatoria")
        if len(ciudad) > 100:
            raise ValueError("La ciudad no puede exceder 100 caracteres")
        if not departamento or len(departamento.strip()) == 0:
            raise ValueError("El departamento es obligatorio")
        if len(departamento) > 100:
            raise ValueError("El departamento no puede exceder 100 caracteres")
        if not pais or len(pais.strip()) == 0:
            raise ValueError("El país es obligatorio")
        if len(pais) > 100:
            raise ValueError("El país no puede exceder 100 caracteres")

        usuario = (
            self.db.query(USUARIOS).filter(USUARIOS.id_usuario == id_usuario).first()
        )
        if not usuario:
            raise ValueError("El usuario especificado no existe")

        if id_usuario_crea is None:
            admin = self.db.query(USUARIOS).filter(USUARIOS.es_admin == True).first()
            if not admin:
                raise ValueError(
                    "No se encontró un usuario administrador para crear la dirección"
                )
            id_usuario_crea = admin.id_usuario

        pais_normalizado = pais.strip().title()
        if pais_normalizado not in PAISES_VALIDOS:
            raise ValueError("El país seleccionado no es válido")
        obj = DIRECCIONES(
            id_usuario=id_usuario,
            direccion=direccion.strip().title(),
            ciudad=ciudad.strip().title(),
            departamento=departamento.strip().title(),
            pais=pais_normalizado,
            id_usuario_crea=id_usuario_crea,
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def obtener_direccion(self, direccion_id: UUID) -> Optional[DIRECCIONES]:
        """
        Obtiene una dirección por su UUID.

        Args:
            direccion_id: UUID de la dirección.

        Returns:
            Instancia de DIRECCIONES si existe, None en caso contrario.
        """
        return self.db.get(DIRECCIONES, direccion_id)

    def obtener_direcciones_usuario(
        self, id_usuario: UUID, skip: int = 0, limit: int = 100
    ) -> List[DIRECCIONES]:
        """
        Lista direcciones filtradas por usuario propietario con paginación.

        Args:
            id_usuario: UUID del usuario.
            skip: Número de registros a omitir.
            limit: Cantidad máxima de registros a retornar.

        Returns:
            Lista de direcciones del usuario indicado.
        """
        return (
            self.db.query(DIRECCIONES)
            .filter(DIRECCIONES.id_usuario == id_usuario)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def obtener_direcciones(self, skip: int = 0, limit: int = 100) -> List[DIRECCIONES]:
        """
        Lista todas las direcciones con paginación.

        Args:
            skip: Número de registros a omitir.
            limit: Cantidad máxima de registros a retornar.

        Returns:
            Lista de instancias de DIRECCIONES.
        """
        return self.db.query(DIRECCIONES).offset(skip).limit(limit).all()

    def actualizar_direccion(
        self, direccion_id: UUID, id_usuario_edita: Optional[UUID] = None, **kwargs
    ) -> Optional[DIRECCIONES]:
        """
        Actualiza una dirección validando campos y referencias.

        Args:
            direccion_id: UUID de la dirección a actualizar.
            id_usuario_edita: UUID del usuario que edita (obligatorio).
            **kwargs: Campos a actualizar (direccion, ciudad, departamento, pais, id_usuario).

        Returns:
            Instancia actualizada de DIRECCIONES, o None si no existe.

        Raises:
            ValueError: Si los datos son inválidos o las referencias no existen.
        """
        obj = self.db.get(DIRECCIONES, direccion_id)
        if not obj:
            return None

        if "direccion" in kwargs:
            direccion = kwargs["direccion"]
            if not direccion or len(direccion.strip()) == 0:
                raise ValueError("La dirección es obligatoria")
            if len(direccion) > 200:
                raise ValueError("La dirección no puede exceder 200 caracteres")
            kwargs["direccion"] = direccion.strip().title()

        if "ciudad" in kwargs:
            ciudad = kwargs["ciudad"]
            if not ciudad or len(ciudad.strip()) == 0:
                raise ValueError("La ciudad es obligatoria")
            if len(ciudad) > 100:
                raise ValueError("La ciudad no puede exceder 100 caracteres")
            kwargs["ciudad"] = ciudad.strip().title()

        if "departamento" in kwargs:
            departamento = kwargs["departamento"]
            if not departamento or len(departamento.strip()) == 0:
                raise ValueError("El departamento es obligatorio")
            if len(departamento) > 100:
                raise ValueError("El departamento no puede exceder 100 caracteres")
            kwargs["departamento"] = departamento.strip().title()

        if "pais" in kwargs:
            pais = kwargs["pais"]
            pais_normalizado = pais.strip().title()
            if pais_normalizado not in PAISES_VALIDOS:
                raise ValueError("El país seleccionado no es válido")
            kwargs["pais"] = pais_normalizado

        if "id_usuario" in kwargs:
            usuario = (
                self.db.query(USUARIOS)
                .filter(USUARIOS.id_usuario == kwargs["id_usuario"])
                .first()
            )
            if not usuario:
                raise ValueError("El usuario especificado no existe")

        if id_usuario_edita is None:
            admin = self.db.query(USUARIOS).filter(USUARIOS.es_admin == True).first()
            if not admin:
                raise ValueError(
                    "No se encontró un usuario administrador para editar la dirección"
                )
            id_usuario_edita = admin.id_usuario

        obj.id_usuario_edita = id_usuario_edita

        for k, v in kwargs.items():
            if hasattr(obj, k):
                setattr(obj, k, v)

        self.db.commit()
        self.db.refresh(obj)
        return obj

    def eliminar_direccion(self, direccion_id: UUID) -> bool:
        """
        Elimina una dirección por su UUID.

        Args:
            direccion_id: UUID de la dirección.

        Returns:
            True si se eliminó correctamente, False si no existe.
        """
        obj = self.db.get(DIRECCIONES, direccion_id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
