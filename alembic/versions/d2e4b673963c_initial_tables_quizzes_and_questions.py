"""Initial tables (quizzes and questions)

Revision ID: d2e4b673963c
Revises: 
Create Date: 2023-11-26 00:32:14.892163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2e4b673963c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quizzes',
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('description', sa.String(length=512), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quizzes_title'), 'quizzes', ['title'], unique=False)
    op.create_table('questions',
    sa.Column('quiz_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(length=256), nullable=False),
    sa.Column('type', sa.String(length=64), nullable=False),
    sa.Column('points', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.current_timestamp(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('questions')
    op.drop_index(op.f('ix_quizzes_title'), table_name='quizzes')
    op.drop_table('quizzes')
    # ### end Alembic commands ###
