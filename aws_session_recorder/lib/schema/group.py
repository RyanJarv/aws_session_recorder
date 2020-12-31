import datetime
import json
from typing import TYPE_CHECKING, Iterator, Any, Union, Optional

from typing import List

import dateutil
import sqlalchemy as sa  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.base import Base, TimeStamp
from aws_session_recorder.lib.schema.identity import InlinePolicy

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

    def __init__(self, resp):
        super().__init__(**resp)

    id: int = sa.Column(sa.Integer, primary_key=True)

    Path: str = sa.Column(sa.String)
    GroupName: str = sa.Column(sa.String)
    GroupId: str = sa.Column(sa.String)
    Arn: dict = sa.Column(sa.String)
    CreateDate: Optional[datetime.datetime] = sa.Column(TimeStamp)

    users: List[Any] = relationship("User", back_populates="groups", secondary=group_membership)

    inline_policies: 'List[GroupPolicy]' = relationship("GroupPolicy", cascade="all, delete-orphan", back_populates="group")


class GroupPolicy(InlinePolicy):
    __tablename__ = "group_policy"

    def __init__(self, resp):
        super().__init__(**resp)

    policy_name = sa.Column(sa.String, sa.ForeignKey('inline_policy.PolicyName'), primary_key=True)
    GroupName = sa.Column(sa.String, sa.ForeignKey('group.GroupName'))

    group: 'List[Group]' = relationship("Group", back_populates="inline_policies")

    __mapper_args__ = {
        'polymorphic_identity': 'group'
    }
