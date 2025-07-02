# Copyright The IETF Trust 2025, All Rights Reserved
import rules


@rules.predicate
def is_rpc_person(user):
    return hasattr(user.datatracker_person(), "rpcperson")


@rules.predicate
def is_comment_author(user, comment):
    return comment.by_id == user.datatracker_person().pk
