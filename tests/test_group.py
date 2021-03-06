"""Tests for `aws_session_recorder.lib.schema.user` package."""

import json

import pytest
import typing

from aws_session_recorder.lib import Session
from aws_session_recorder.lib.schema.group import Group, GroupPolicy
from aws_session_recorder.lib.schema.user import User
from tests.test_base import test_policy_doc, group_name

# These are used by pytest
from tests.test_base import session, iam, group, user  # noqa: F401

if typing.TYPE_CHECKING:
    from mypy_boto3_iam.client import IAMClient  # type: ignore
    from mypy_boto3_iam import type_defs as t  # type: ignore

group_name2 = group_name + "2"


def test_group(session, group: 't.GetUserResponseTypeDef'):
    g: Group = session.db.query(Group).all()[0]
    assert group['Group']['Arn'] == g.Arn


@pytest.fixture(scope='function')
def group2(iam) -> 't.GetUserResponseTypeDef':
    iam.create_group(GroupName=group_name2)
    return iam.get_group(GroupName=group_name2)


def test_group2(session: Session, group, group2):
    assert session.db.query(Group).count() == 2
    assert group_name == session.db.query(Group).all()[0].GroupName
    assert group_name2 == session.db.query(Group).all()[1].GroupName


@pytest.fixture(scope='function')
def list_groups(session: Session, iam: 'IAMClient') -> 't.ListGroupsResponseTypeDef':
    assert 0 == session.db.query(Group).count()
    iam.create_group(GroupName=group_name)
    iam.create_group(GroupName=group_name2)
    return iam.list_groups()


def test_list_groups(session: Session, list_groups: 't.ListGroupsResponseTypeDef'):
    assert len(list_groups['Groups']) == session.db.query(Group).count()
    assert len(list_groups['Groups']) == 2


def test_group_has_users(session, group: 't.GetUserResponseTypeDef'):
    db_grp: Group = session.db.query(Group).all()[0]
    assert group['Users'][0]['Arn'] == db_grp.users[0].Arn


def test_user_has_group(session, group: 't.GetUserResponseTypeDef'):
    usr: User = session.db.query(User).all()[0]
    db_group: Group = usr.groups[0]
    assert group['Group']['Arn'] == db_group.Arn


@pytest.fixture(scope='function')
def inline_group_policy_list(iam: 'IAMClient', group: 't.GetUserResponseTypeDef') -> 't.ListGroupPoliciesResponseTypeDef':
    iam.put_group_policy(GroupName=group_name, PolicyName='test_policy', PolicyDocument=test_policy_doc)
    return iam.list_group_policies(GroupName=group_name)


def test_inline_group_policy_list(session: Session, inline_group_policy_list: 't.ListGroupPoliciesResponseTypeDef'):
    assert inline_group_policy_list['PolicyNames'][0] == session.db.query(GroupPolicy).first().PolicyName


def test_inline_group_policy_list_by_group(session: Session, inline_group_policy_list: 't.ListGroupPoliciesResponseTypeDef'):
    live_name = inline_group_policy_list['PolicyNames'][0]
    group: Group = session.db.query(Group).first()
    assert live_name == group.inline_policies[0].PolicyName


# Listing updates the record but doesn't have a PolicyDocument associated with it, so make sure we don't delete the
# one that already exists with GetUserPolicy.
def test_inline_group_policy_get_then_list(session: Session, inline_group_policy: 't.GetUserPolicyResponseTypeDef',
                                           inline_group_policy_list: 't.ListUserPoliciesResponseTypeDef'):
    # TODO: Return hash with UserPolicy.PolicyDocument
    assert inline_group_policy['PolicyDocument'] == json.loads(session.db.query(GroupPolicy).first().PolicyDocument)


@pytest.fixture(scope='function')
def inline_group_policy(iam, group) -> 't.GetGroupPolicyResponseTypeDef':
    iam.put_group_policy(GroupName=group_name, PolicyName='test_policy', PolicyDocument=test_policy_doc)
    return iam.get_group_policy(GroupName=group_name, PolicyName='test_policy')


def test_inline_group_policy(session, inline_group_policy: 't.GetGroupPolicyResponseTypeDef'):
    assert inline_group_policy['PolicyName'] == session.db.query(GroupPolicy).first().PolicyName


def test_inline_group_policy_by_group(session, inline_group_policy: 't.GetGroupPolicyResponseTypeDef'):
    live_name = inline_group_policy['PolicyName']
    group: Group = session.db.query(Group).first()
    assert live_name == group.inline_policies[0].PolicyName


def test_inline_group_policy_document(session, inline_group_policy: 't.GetGroupPolicyResponseTypeDef'):
    live_doc = json.dumps(inline_group_policy['PolicyDocument'])
    # TODO: Fix this edge case
    db_doc = json.dumps(json.loads(session.db.query(GroupPolicy).first().PolicyDocument))
    assert live_doc == db_doc
