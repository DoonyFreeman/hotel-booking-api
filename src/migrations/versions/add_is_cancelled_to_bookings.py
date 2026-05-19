"""add is_cancelled to bookings

Revision ID: add_is_cancelled
Revises: 704574d025af
Create Date: 2026-05-19 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_is_cancelled"
down_revision: Union[str, Sequence[str], None] = "704574d025af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bookings",
        sa.Column("is_cancelled", sa.Boolean(), server_default="false", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("bookings", "is_cancelled")
