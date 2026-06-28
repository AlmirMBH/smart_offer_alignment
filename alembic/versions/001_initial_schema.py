"""Initial schema."""

from alembic import op
import sqlalchemy as sa


revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("component", sa.String(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_offers_component", "offers", ["component"])

    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("component", sa.String(), nullable=False),
        sa.Column("embed_text", sa.Text(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=False),
    )
    op.create_index("ix_items_component", "items", ["component"])

    op.create_table(
        "offer_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("offer_id", sa.Integer(), sa.ForeignKey("offers.id"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("items.id"), nullable=False),
        sa.Column("source_sheet", sa.String(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit_price", sa.Float(), nullable=True),
        sa.Column("total_price", sa.Float(), nullable=True),
        sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("auto_approved", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(), primary_key=True),
        sa.Column("value", sa.String(), nullable=False),
    )


def downgrade():
    op.drop_table("app_settings")
    op.drop_table("offer_items")
    op.drop_index("ix_items_component", "items")
    op.drop_table("items")
    op.drop_index("ix_offers_component", "offers")
    op.drop_table("offers")
