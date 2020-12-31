import json

"""Tests for `aws_session_recorder.lib.schema.user` package."""
from aws_session_recorder.lib.schema.group import Group, GroupPolicy
from aws_session_recorder.lib.schema.user import User
from tests.test_base import *


def test_group(session, group: t.GetGroupResponseTypeDef):
    g: Group = session.db.query(Group).all()[0]
    assert group['Group']['Arn'] == g.Arn


def test_group_has_users(session, group: t.GetGroupResponseTypeDef):
    db_grp: Group = session.db.query(Group).all()[0]
    assert group['Users'][0]['Arn'] == db_grp.users[0].Arn


def test_user_has_group(session, group: t.GetGroupResponseTypeDef):
    usr: User = session.db.query(User).all()[0]
    db_group: Group = usr.groups[0]
    assert group['Group']['Arn'] == db_group.Arn


@pytest.fixture(scope='function')
def inline_group_policy(iam, group) -> t.GetGroupPolicyResponseTypeDef:
    iam.put_group_policy(GroupName=group_name, PolicyName='test_policy', PolicyDocument=test_policy)
    return iam.get_group_policy(GroupName=group_name, PolicyName='test_policy')


def test_inline_group_policy(session, inline_group_policy: t.GetGroupPolicyResponseTypeDef):
    assert inline_group_policy['PolicyName'] == session.db.query(GroupPolicy).first().PolicyName

def test_inline_group_policy_by_group(session, inline_group_policy: t.GetGroupPolicyResponseTypeDef):
    live_name = inline_group_policy['PolicyName']
    group: Group = session.db.query(Group).first()
    assert live_name == group.inline_policies[0].PolicyName

def test_inline_group_policy_document(session, inline_group_policy: t.GetGroupPolicyResponseTypeDef):
    live_doc = json.dumps(inline_group_policy['PolicyDocument'])
    # TODO: Fix this edge case
    db_doc = json.dumps(json.loads(session.db.query(GroupPolicy).first().PolicyDocument))
    assert live_doc == db_doc