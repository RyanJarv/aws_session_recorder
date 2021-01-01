import datetime
from typing import TYPE_CHECKING

from typing import List

import dateutil
import sqlalchemy as sa  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy_utils import JSONType  # type: ignore

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.base import Base, TimeStamp
#from aws_session_recorder.lib.schema.policy import policy_attachments

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()


class Identity(Base):
    def __init__(self, resp):
        super().__init__(**resp)

    __tablename__ = "identity"

    id: int = sa.Column(sa.Integer, unique=True, autoincrement=True)

    Path: str = sa.Column(sa.String)
    Arn: str = sa.Column(sa.String, primary_key=True)
    CreateDate: datetime.datetime = sa.Column(TimeStamp)
    Tags: List[t.TagTypeDef] = sa.Column(JSONType)

    #attached_policies = relationship("Policy", secondary=policy_attachments)

    type: str = sa.Column(sa.String(20))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'identity'
    }


class InlinePolicy(Base):
    __tablename__ = "inline_policy"

    id: int = sa.Column(sa.Integer, unique=True)

    PolicyName = sa.Column(sa.String, primary_key=True)
    PolicyDocument = sa.Column(JSONType)

    type: str = sa.Column(sa.String(20), primary_key=True)

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'inline'
    }
