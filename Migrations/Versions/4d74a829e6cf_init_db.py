"""init db

Revision ID: 4d74a829e6cf
Revises:
Create Date: 2025-09-20 20:05:44.588174

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4d74a829e6cf"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "roles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nombre", sa.String(length=50), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sexo",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("codigo", sa.String(length=1), nullable=False),
        sa.Column("nombre", sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo"),
    )

    op.create_table(
        "tipo_documento",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nombre", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. Usuarios (depende de roles, sexo y tipo_documento)
    op.create_table(
        "usuarios",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("apellido", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("id_sexo", sa.UUID(), nullable=True),
        sa.Column("id_tipo_documento", sa.UUID(), nullable=True),
        sa.Column("numero_documento", sa.String(length=20), nullable=False),
        sa.Column("id_rol", sa.UUID(), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=True),
        sa.Column("id_usuario_crea", sa.UUID(), nullable=False),
        sa.Column("id_usuario_edita", sa.UUID(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_edicion", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["id_rol"], ["roles.id"]),
        sa.ForeignKeyConstraint(["id_sexo"], ["sexo.id"]),
        sa.ForeignKeyConstraint(["id_tipo_documento"], ["tipo_documento.id"]),
        sa.ForeignKeyConstraint(["id_usuario_crea"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_edita"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("numero_documento"),
    )

    # 3. Tablas dependientes de usuarios
    op.create_table(
        "carritos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("id_usuario", sa.UUID(), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=True),
        sa.Column("id_usuario_crea", sa.UUID(), nullable=False),
        sa.Column("id_usuario_edita", sa.UUID(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_edicion", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_crea"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_edita"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "categorias",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.String(length=255), nullable=True),
        sa.Column("id_usuario_crea", sa.UUID(), nullable=False),
        sa.Column("id_usuario_edita", sa.UUID(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_edicion", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["id_usuario_crea"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_edita"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "descuentos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("codigo", sa.String(length=50), nullable=False),
        sa.Column("porcentaje", sa.Float(), nullable=False),
        sa.Column("fecha_inicio", sa.DateTime(), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=True),
        sa.Column("id_usuario_crea", sa.UUID(), nullable=False),
        sa.Column("id_usuario_edita", sa.UUID(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_edicion", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["id_usuario_crea"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_edita"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo"),
    )

    op.create_table(
        "direcciones",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("id_usuario", sa.UUID(), nullable=True),
        sa.Column("direccion", sa.String(length=255), nullable=False),
        sa.Column("ciudad", sa.String(length=100), nullable=False),
        sa.Column("codigo_postal", sa.String(length=20), nullable=True),
        sa.Column("pais", sa.String(length=100), nullable=False),
        sa.Column("principal", sa.Boolean(), nullable=True),
        sa.Column("id_usuario_crea", sa.UUID(), nullable=False),
        sa.Column("id_usuario_edita", sa.UUID(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_edicion", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_crea"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_edita"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "productos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nombre", sa.String(length=100), nullable=False),
        sa.Column("descripcion", sa.String(length=500), nullable=True),
        sa.Column("precio", sa.Float(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column("id_categoria", sa.UUID(), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=True),
        sa.Column("id_usuario_crea", sa.UUID(), nullable=False),
        sa.Column("id_usuario_edita", sa.UUID(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_edicion", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["id_categoria"], ["categorias.id"]),
        sa.ForeignKeyConstraint(["id_usuario_crea"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_edita"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "pedidos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("id_usuario", sa.UUID(), nullable=True),
        sa.Column("id_direccion", sa.UUID(), nullable=True),
        sa.Column("id_descuento", sa.UUID(), nullable=True),
        sa.Column("fecha_pedido", sa.DateTime(), nullable=False),
        sa.Column("estado", sa.String(length=50), nullable=False),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column("id_usuario_crea", sa.UUID(), nullable=False),
        sa.Column("id_usuario_edita", sa.UUID(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_edicion", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["id_descuento"], ["descuentos.id"]),
        sa.ForeignKeyConstraint(["id_direccion"], ["direcciones.id"]),
        sa.ForeignKeyConstraint(["id_usuario"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_crea"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_edita"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "carrito_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("id_carrito", sa.UUID(), nullable=True),
        sa.Column("id_producto", sa.UUID(), nullable=True),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("id_usuario_crea", sa.UUID(), nullable=False),
        sa.Column("id_usuario_edita", sa.UUID(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_edicion", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["id_carrito"], ["carritos.id"]),
        sa.ForeignKeyConstraint(["id_producto"], ["productos.id"]),
        sa.ForeignKeyConstraint(["id_usuario_crea"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_edita"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "facturas",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("id_pedido", sa.UUID(), nullable=True),
        sa.Column("numero_factura", sa.String(length=100), nullable=False),
        sa.Column("fecha_emision", sa.DateTime(), nullable=False),
        sa.Column("subtotal", sa.Float(), nullable=False),
        sa.Column("impuesto", sa.Float(), nullable=False),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column("id_usuario_crea", sa.UUID(), nullable=False),
        sa.Column("id_usuario_edita", sa.UUID(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_edicion", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["id_pedido"], ["pedidos.id"]),
        sa.ForeignKeyConstraint(["id_usuario_crea"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_edita"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("numero_factura"),
    )

    op.create_table(
        "pedido_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("id_pedido", sa.UUID(), nullable=True),
        sa.Column("id_producto", sa.UUID(), nullable=True),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("precio_unitario", sa.Float(), nullable=False),
        sa.Column("id_usuario_crea", sa.UUID(), nullable=False),
        sa.Column("id_usuario_edita", sa.UUID(), nullable=True),
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("fecha_edicion", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["id_pedido"], ["pedidos.id"]),
        sa.ForeignKeyConstraint(["id_producto"], ["productos.id"]),
        sa.ForeignKeyConstraint(["id_usuario_crea"], ["usuarios.id"]),
        sa.ForeignKeyConstraint(["id_usuario_edita"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("pedido_items")
    op.drop_table("facturas")
    op.drop_table("carrito_items")
    op.drop_table("pedidos")
    op.drop_table("productos")
    op.drop_table("direcciones")
    op.drop_table("descuentos")
    op.drop_table("categorias")
    op.drop_table("carritos")
    op.drop_table("usuarios")
    op.drop_table("tipo_documento")
    op.drop_table("sexo")
    op.drop_table("roles")
