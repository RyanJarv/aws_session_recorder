import json
from typing import Iterator

"""Tests for `aws_session_recorder.lib.schema.user` package."""
from aws_session_recorder.lib.schema.role import InstanceProfile
from tests.test_base import *


def test_instance_profile(session: Session, instance_profile: t.GetInstanceProfileResponseTypeDef):
    assert instance_profile['InstanceProfile']['Arn'] == session.db.query(InstanceProfile).first().Arn


# #TODO: Unsure what the best way to populate role's off this data is right now
# def test_instance_profile_role(session: Session, instance_profile: t.GetInstanceProfileResponseTypeDef):
#     assert instance_profile['InstanceProfile']['Roles'][0]['Arn'] == session.db.query(Role).first().Arn



