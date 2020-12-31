import json
from typing import Iterator

"""Tests for `aws_session_recorder.lib.schema.user` package."""
from aws_session_recorder.lib.schema.policy import Policy, PolicyVersion
from tests.test_base import *


# TODO: Test attachments
def test_policy(session, policy: t.GetPolicyResponseTypeDef):
    policy = policy['Policy']
    for key, value in policy.items():
        # TODO: Use datetime object in db
        # if key in ['UpdateDate']:
        #     value = str(value)

        # TODO: Look into why the db records 0 instead of 1 here
        if key == 'AttachmentCount':
            continue
        assert value == getattr(session.db.query(Policy).all()[0], key)


@pytest.fixture(scope='function')
def list_policies(session: Session, iam: IAMClient) -> t.ListPoliciesResponseTypeDef:
    assert 0 == session.db.query(Policy).count()
    iam.create_policy(PolicyName='test_policy', PolicyDocument=test_policy_doc)
    iam.create_policy(PolicyName='test_policy2', PolicyDocument=test_policy_doc)
    return iam.list_policies(Scope='Local')


def test_list_policies(session: Session, list_policies: t.ListPoliciesResponseTypeDef):
    assert len(list_policies['Policies']) == session.db.query(Policy).count()
    assert len(list_policies['Policies']) == 2


@pytest.fixture(scope='function')
def policy_version(iam: IAMClient, policy: t.GetPolicyResponseTypeDef) -> t.GetPolicyVersionResponseTypeDef:
    policy_arn = policy['Policy']['Arn']
    resp: t.ListPolicyVersionsResponseTypeDef = iam.list_policy_versions(PolicyArn=policy_arn)
    first_version = resp['Versions'][0]['VersionId']
    return iam.get_policy_version(PolicyArn=policy_arn, VersionId=first_version)


def test_policy_version(session: Session, policy_version: t.GetPolicyVersionResponseTypeDef):
    assert policy_version['PolicyVersion']['VersionId'] == session.db.query(PolicyVersion).first().VersionId



