import pytest

def test_engine_import():
    try:
        from pyknow import engine
    except ImportError as exc:
        assert False, exc
    else:
        assert True


def test_KnowledgeEngine_exists():
    from pyknow import engine
    assert hasattr(engine, 'KnowledgeEngine')


def test_KnowledgeEngine_is_class():
    from pyknow import engine
    assert isinstance(engine.KnowledgeEngine, type)


def test_KnowledgeEngine_has__facts():
    from pyknow.engine import KnowledgeEngine
    ke = KnowledgeEngine()
    assert hasattr(ke, '_facts')


def test_KnowledgeEngine_has_asrt():
    from pyknow.engine import KnowledgeEngine
    ke = KnowledgeEngine()
    assert hasattr(ke, 'asrt')


def test_KnowledgeEngine_asrt_define_fact():
    from pyknow.engine import KnowledgeEngine
    ke = KnowledgeEngine()
    ke.asrt('test', True)
    assert ke._facts['test'] is True


def test_KnowledgeEngine_asrt_cant_define_twice():
    from pyknow.engine import KnowledgeEngine, DuplicatedFactError

    ke = KnowledgeEngine()
    ke.asrt('test', True)

    with pytest.raises(DuplicatedFactError):
        ke.asrt('test', True)


def test_KnowledgeEngine_getitem_asserted():
    from pyknow.engine import KnowledgeEngine

    ke = KnowledgeEngine()

    ke.asrt('NAME', 'VALUE')

    assert ke['NAME'] == 'VALUE'


def test_KnowledgeEngine_getitem_not_asserted():
    from pyknow.engine import KnowledgeEngine

    ke = KnowledgeEngine()

    with pytest.raises(KeyError):
        ke['NAME']


def test_KnowledgeEngine__contains__True():
    from pyknow.engine import KnowledgeEngine

    ke = KnowledgeEngine()
    ke.asrt('name', 'value')

    assert 'name' in ke


def test_KnowledgeEngine__contains__False():
    from pyknow.engine import KnowledgeEngine

    ke = KnowledgeEngine()

    assert 'name' not in ke


def test_KnowledgeEngine_has_retract():
    from pyknow.engine import KnowledgeEngine

    assert hasattr(KnowledgeEngine, 'retract')


def test_KnowledgeEngine_retract_assertion():
    from pyknow.engine import KnowledgeEngine

    ke = KnowledgeEngine()
    ke.asrt('something', 'SOMETHING')
    ke.retract('something')

    assert 'something' not in ke


def test_KnowledgeEngine_retract_empty():
    from pyknow.engine import KnowledgeEngine

    ke = KnowledgeEngine()

    ke.retract('something')

    assert 'something' not in ke


def test_KnowledgeEngine_has_agenda():
    from pyknow.engine import KnowledgeEngine
    ke = KnowledgeEngine()
    assert hasattr(ke, 'agenda')


def test_KnowledgeEngine_has_run():
    from pyknow.engine import KnowledgeEngine
    assert hasattr(KnowledgeEngine, 'run')


def test_KnowledgeEngine_run_set_running():
    from pyknow.engine import KnowledgeEngine

    ke = KnowledgeEngine()
    assert not ke.running

    ke.run()
    assert ke.running


def test_KnowledgeEngine_has_reset():
    from pyknow.engine import KnowledgeEngine
    assert hasattr(KnowledgeEngine, 'reset')


def test_KnowledgeEngine_reset_resets_running():
    from pyknow.engine import KnowledgeEngine
    ke = KnowledgeEngine()

    ke.run()
    assert ke.running

    ke.reset()
    assert not ke.running


def test_KnowledgeEngine_reset_resets_agenda():
    from pyknow.engine import KnowledgeEngine
    ke = KnowledgeEngine()
    ke.agenda = None

    ke.reset()
    assert ke.agenda is not None


def test_KnowledgeEngine_reset_resets_facts():
    from pyknow.engine import KnowledgeEngine
    ke = KnowledgeEngine()
    ke._facts = None

    ke.reset()
    assert ke._facts is not None

@pytest.mark.wip
def test_KnowledgeEngine_get_matching_rules_exists():
    from pyknow.engine import KnowledgeEngine

    assert hasattr(KnowledgeEngine, 'get_matching_rules')


@pytest.mark.wip
def test_KnowledgeEngine_get_matching_rules_returns_dict():
    from pyknow.engine import KnowledgeEngine

    ke = KnowledgeEngine()

    assert isinstance(ke.get_matching_rules(), dict)


@pytest.mark.wip
def test_KnowledgeEngine_get_matching_rules__no_rules():
    from pyknow.engine import KnowledgeEngine

    ke = KnowledgeEngine()

    assert ke.get_matching_rules() == {}


@pytest.mark.wip
def test_KnowledgeEngine_get_matching_rules__matching_rule():
    from pyknow.engine import KnowledgeEngine
    from pyknow.rule import AND
    from pyknow.rule import FactState as fs

    class Test(KnowledgeEngine):
        @AND(fact1=fs.NOT_DEFINED)
        def myrule(self):
            pass

    ke = Test()
    matching_rules = ke.get_matching_rules()

    assert 'myrule' in matching_rules


@pytest.mark.wip
def test_KnowledgeEngine_get_matching_rules__multiple_match():
    from pyknow.engine import KnowledgeEngine
    from pyknow.rule import AND
    from pyknow.rule import FactState as fs

    class Test(KnowledgeEngine):
        @AND(fact1=fs.NOT_DEFINED)
        def myrule1(self):
            pass

        @AND(fact2=fs.NOT_DEFINED)
        def myrule2(self):
            pass

        @AND(fact3=fs.DEFINED)
        def myrule3(self):
            pass

    ke = Test()
    matching_rules = ke.get_matching_rules()

    assert 'myrule1' in matching_rules
    assert 'myrule2' in matching_rules
    assert 'myrule3' not in matching_rules


@pytest.mark.wip
def test_KnowledgeEngine_default_strategy_is_Depth():
    from pyknow.engine import KnowledgeEngine
    from pyknow.strategies import Depth

    assert isinstance(KnowledgeEngine.strategy, Depth)


@pytest.mark.wip
def test_KnowledgeEngine_run_1_modify_agenda_if_needed():
    from pyknow.engine import KnowledgeEngine
    from pyknow.rule import AND
    from pyknow.rule import FactState as fs
    
    class Test(KnowledgeEngine):
        @AND(fact1=fs.DEFINED)
        def rule1(self):
            self.asrt('fact2', True)

        @AND(fact2=fs.DEFINED)
        def rule2(self):
            pass

    ke = Test()
    current_agenda = ke.agenda
    ke.asrt('fact1', True)
    ke.run(1)

    assert current_agenda != ke.agenda


@pytest.mark.wip
def test_KnowledgeEngine_run_consumes_agenda():
    from pyknow.engine import KnowledgeEngine
    from pyknow.rule import AND
    from pyknow.rule import FactState as fs
    
    executed = False
    class Test(KnowledgeEngine):
        @AND(fact1=fs.DEFINED)
        def rule1(self):
            executed = True

    ke = Test()
    current_agenda = ke.agenda
    ke.asrt('fact1', True)
    ke.run()  # If this runs forever, then run is not consuming the agenda.

    assert executed