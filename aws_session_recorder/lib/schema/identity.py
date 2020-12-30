from typing import TYPE_CHECKING

from typing import List

import sqlalchemy as sa  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from sqlalchemy_utils import JSONType  # type: ignore

from aws_session_recorder.lib.helpers import AlwaysDoNothing
from aws_session_recorder.lib.schema.base import Base
from aws_session_recorder.lib.schema.policy import policy_attachments

if TYPE_CHECKING:
    from mypy_boto3_iam import type_defs as t  # type: ignore
else:
    t = AlwaysDoNothing()
    client = AlwaysDoNothing()

class Identity(Base):
    def __init__(self, resp):
        super().__init__(**resp)

    __tablename__ = "identity"

    id: int = sa.Column(sa.Integer, unique=True)

    Path: str = sa.Column(sa.String)
    Arn: str = sa.Column(sa.String, primary_key=True)
    CreateDate: str = sa.Column(sa.String)
    Tags: List[t.TagTypeDef] = sa.Column(JSONType)

    attached_policies = relationship("Policy", secondary=policy_attachments)

    type: str = sa.Column(sa.String(20))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'identity'
    }

