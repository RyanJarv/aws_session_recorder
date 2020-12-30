import json
from typing import TYPE_CHECKING, Iterator, Any, Union

from typing import List

import sqlalchemy as sa  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy_utils import JSONType  # type: ignore

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.base import Base
from aws_session_recorder.lib.schema.policy import policy_attachments, UserPolicy

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()

group_membership = sa.Table('group_membership', Base.metadata,
                            sa.Column('user_id', sa.String, sa.ForeignKey('user.arn')),
                            sa.Column('group_id', sa.Integer, sa.ForeignKey('group.id')),
                            )

class Group(Base):
    __tablename__ = "group"

    def __init__(self, key: t.GroupTypeDef):
        super().__init__(**key)

    id: int = sa.Column(sa.Integer, primary_key=True)

    Path: str = sa.Column(sa.String)
    GroupName: str = sa.Column(sa.String)
    GroupId: str = sa.Column(sa.String)
    Arn: dict = sa.Column(sa.String)
    CreateDate: str = sa.Column(sa.String)

    users: List[Any] = relationship("User", back_populates="groups", secondary=group_membership)

