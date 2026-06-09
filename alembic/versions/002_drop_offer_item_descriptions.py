"""Drop parent and child description from offer_items."""

from alembic import op
import sqlalchemy as sa


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("offer_items") as batch_op:
        batch_op.drop_column("child_description")
        batch_op.drop_column("parent_description")


def downgrade():
    with op.batch_alter_table("offer_items") as batch_op:
        batch_op.add_column(sa.Column("parent_description", sa.Text(), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("child_description", sa.Text(), nullable=False, server_default=""))
