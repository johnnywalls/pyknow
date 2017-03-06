import pytest


@pytest.mark.wip
def test_ordinarymatchnode_exists():
    try:
        from pyknow.rete.nodes import OrdinaryMatchNode
    except ImportError as exc:
        assert False, exc


@pytest.mark.wip
def test_ordinarymatchnode_is_abstractnode():
    from pyknow.rete.nodes import OrdinaryMatchNode
    from pyknow.rete.abstract import TwoInputNode

    assert issubclass(OrdinaryMatchNode, TwoInputNode)


@pytest.mark.wip
def test_ordinarymatchnode_accepts_callable():
    from pyknow.rete.nodes import OrdinaryMatchNode

    # MUST NOT RAISE
    OrdinaryMatchNode(lambda l, r: True)

    with pytest.raises(TypeError):
        OrdinaryMatchNode('NONCALLABLE')


@pytest.mark.wip
def test_ordinarymatchnode_left_activate_valid_store_in_left_memory():
    from pyknow.rete.nodes import OrdinaryMatchNode
    from pyknow.rete.token import Token
    from pyknow.fact import Fact

    omn = OrdinaryMatchNode(lambda l, r: True)

    assert not omn.left_memory

    fact = Fact(test='data')
    token = Token.valid(fact)
    omn.activate_left(token)

    assert ({fact}, {}) in omn.left_memory


@pytest.mark.wip
def test_ordinarymatchnode_left_activate_valid_build_new_tokens(TestNode):
    from pyknow.rete.nodes import OrdinaryMatchNode
    from pyknow.rete.token import Token
    from pyknow.fact import Fact

    omn = OrdinaryMatchNode(lambda l, r: True)
    tn1 = TestNode()
    tn2 = TestNode()
    omn.add_child(tn1, tn1.activate)
    omn.add_child(tn2, tn2.activate)

    rt1 = Token.valid(Fact(rightdata='rightdata1'))
    rt2 = Token.valid(Fact(rightdata='rightdata2'))
    omn.right_memory.append((rt1.data, rt1.context))
    omn.right_memory.append((rt2.data, rt2.context))

    token = Token.valid(Fact(leftdata='leftdata'))
    omn.activate_left(token)

    assert tn1.added == [Token.valid([Fact(leftdata='leftdata'),
                                      Fact(rightdata='rightdata1')]),
                         Token.valid([Fact(leftdata='leftdata'),
                                      Fact(rightdata='rightdata2')])]

    assert tn2.added == [Token.valid([Fact(leftdata='leftdata'),
                                      Fact(rightdata='rightdata1')]),
                         Token.valid([Fact(leftdata='leftdata'),
                                      Fact(rightdata='rightdata2')])]


@pytest.mark.wip
def test_ordinarymatchnode_left_activate_invalid_remove_from_left_memory():
    from pyknow.rete.nodes import OrdinaryMatchNode
    from pyknow.rete.token import Token
    from pyknow.fact import Fact

    omn = OrdinaryMatchNode(lambda l, r: True)

    fact = Fact(test='data')
    token = Token.valid(fact)
    omn.left_memory.append((token.data, token.context))

    omn.activate_left(Token.invalid(fact))

    assert not omn.left_memory


@pytest.mark.wip
def test_ordinarymatchnode_left_activate_invalid_build_new_tokens(TestNode):
    from pyknow.rete.nodes import OrdinaryMatchNode
    from pyknow.rete.token import Token
    from pyknow.fact import Fact

    omn = OrdinaryMatchNode(lambda l, r: True)
    tn1 = TestNode()
    tn2 = TestNode()
    omn.add_child(tn1, tn1.activate)
    omn.add_child(tn2, tn2.activate)

    rt1 = Token.valid(Fact(rightdata='rightdata1'))
    rt2 = Token.valid(Fact(rightdata='rightdata2'))
    omn.right_memory.append((rt1.data, rt1.context))
    omn.right_memory.append((rt2.data, rt2.context))

    token = Token.invalid(Fact(leftdata='leftdata'))
    omn.activate_left(token)

    assert tn1.added == [Token.invalid([Fact(leftdata='leftdata'),
                                        Fact(rightdata='rightdata1')]),
                         Token.invalid([Fact(leftdata='leftdata'),
                                        Fact(rightdata='rightdata2')])]

    assert tn2.added == [Token.invalid([Fact(leftdata='leftdata'),
                                        Fact(rightdata='rightdata1')]),
                         Token.invalid([Fact(leftdata='leftdata'),
                                        Fact(rightdata='rightdata2')])]


@pytest.mark.wip
def test_ordinarymatchnode_right_activate_valid_store_in_right_memory():
    from pyknow.rete.nodes import OrdinaryMatchNode
    from pyknow.rete.token import Token
    from pyknow.fact import Fact

    omn = OrdinaryMatchNode(lambda l, r: True)

    assert not omn.right_memory

    fact = Fact(test='data')
    token = Token.valid(fact)
    omn.activate_right(token)

    assert ({fact}, {}) in omn.right_memory


@pytest.mark.wip
def test_ordinarymatchnode_right_activate_valid_build_new_tokens(TestNode):
    from pyknow.rete.nodes import OrdinaryMatchNode
    from pyknow.rete.token import Token
    from pyknow.fact import Fact

    omn = OrdinaryMatchNode(lambda l, r: True)
    tn1 = TestNode()
    tn2 = TestNode()
    omn.add_child(tn1, tn1.activate)
    omn.add_child(tn2, tn2.activate)

    lt1 = Token.valid(Fact(leftdata='leftdata1'))
    lt2 = Token.valid(Fact(leftdata='leftdata2'))
    omn.left_memory.append((lt1.data, lt1.context))
    omn.left_memory.append((lt2.data, lt2.context))

    token = Token.valid(Fact(rightdata='rightdata'))
    omn.activate_right(token)

    assert tn1.added == [Token.valid([Fact(rightdata='rightdata'),
                                      Fact(leftdata='leftdata1')]),
                         Token.valid([Fact(rightdata='rightdata'),
                                      Fact(leftdata='leftdata2')])]

    assert tn2.added == [Token.valid([Fact(rightdata='rightdata'),
                                      Fact(leftdata='leftdata1')]),
                         Token.valid([Fact(rightdata='rightdata'),
                                      Fact(leftdata='leftdata2')])]


@pytest.mark.wip
def test_ordinarymatchnode_right_activate_invalid_remove_from_right_memory():
    from pyknow.rete.nodes import OrdinaryMatchNode
    from pyknow.rete.token import Token
    from pyknow.fact import Fact

    omn = OrdinaryMatchNode(lambda l, r: True)

    fact = Fact(test='data')
    token = Token.valid(fact)
    omn.right_memory.append((token.data, token.context))

    omn.activate_right(Token.invalid(fact))

    assert not omn.right_memory


@pytest.mark.wip
def test_ordinarymatchnode_right_activate_invalid_build_new_tokens(TestNode):
    from pyknow.rete.nodes import OrdinaryMatchNode
    from pyknow.rete.token import Token
    from pyknow.fact import Fact

    omn = OrdinaryMatchNode(lambda l, r: True)
    tn1 = TestNode()
    tn2 = TestNode()
    omn.add_child(tn1, tn1.activate)
    omn.add_child(tn2, tn2.activate)

    rt1 = Token.valid(Fact(leftdata='leftdata1'))
    rt2 = Token.valid(Fact(leftdata='leftdata2'))
    omn.left_memory.append((rt1.data, rt1.context))
    omn.left_memory.append((rt2.data, rt2.context))

    token = Token.invalid(Fact(rightdata='rightdata'))
    omn.activate_right(token)

    assert tn1.added == [Token.invalid([Fact(rightdata='rightdata'),
                                        Fact(leftdata='leftdata1')]),
                         Token.invalid([Fact(rightdata='rightdata'),
                                        Fact(leftdata='leftdata2')])]

    assert tn2.added == [Token.invalid([Fact(rightdata='rightdata'),
                                        Fact(leftdata='leftdata1')]),
                         Token.invalid([Fact(rightdata='rightdata'),
                                        Fact(leftdata='leftdata2')])]