import sys
from unittest import TestCase

from mock import MagicMock

import bouncebox.core.component as bc
import bouncebox.core.event as be
import bouncebox.core.mixins as mixins

class TestBubbleDown(bc.PreMixComponent):
    pass

mixins.component_mixin(TestBubbleDown, mixins.BubbleDownMixin)

class TestBubbleDownMixin(TestCase):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    def runTest(self):
        pass

    def setUp(self):
        pass

    def test_bubble_down(self):
        parent = TestBubbleDown()
        mid = TestBubbleDown()
        child = TestBubbleDown()

        child.add_event_listener(be.Event, 'handle_event')
        child.handle_event = MagicMock()

        # We have an order issue
        parent.add_component(mid)
        mid.add_component(child, contained=True)
        mid.enable_bubble_down(child)

        evt = be.Event()
        parent.broadcast(evt)
        # middle ware should have progated events to child
        child.handle_event.assert_called_once_with(evt)

    def test_bubble_down_hook(self):
        """
            Test the bubble_down keyword for add_component
        """
        parent = TestBubbleDown()
        mid = TestBubbleDown()
        child = TestBubbleDown()

        child.add_event_listener(be.Event, 'handle_event')
        child.handle_event = MagicMock()

        # We have an order issue
        parent.add_component(mid)
        mid.add_component(child, bubble_down=True)

        evt = be.Event()
        parent.broadcast(evt)
        # middle ware should have progated events to child
        child.handle_event.assert_called_once_with(evt)

    def test_bubble_down_hook_error(self):
        """
        Test that you can only enable_bubble_down once
        """
        parent = TestBubbleDown()
        mid = TestBubbleDown()
        child = TestBubbleDown()

        child.add_event_listener(be.Event, 'handle_event')
        child.handle_event = MagicMock()

        # We have an order issue
        parent.add_component(mid)
        mid.add_component(child, bubble_down=True)
        try:
            mid.enable_bubble_down(child)
        except:
            pass
        else:
            assert False, "This should error"

class TestComponentMixin(TestCase):

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)

    def runTest(self):
        pass

    def setUp(self):
        class TestBase(bc.PreMixComponent):
            pass
        self.base = TestBase

    def test_premix_comp(self):
        """
            Test that PreMixComponent is unmixed
        """
        base = self.base
        assert not hasattr(base, '_mixins_')

    def test_component_mixin_add_twice(self):
        """
        Verify that a Mixin will only be added once
        """
        base = self.base
        res = mixins.component_mixin(base, mixins.BubbleDownMixin)
        assert res
        assert 'BubbleDownMixin' in base._mixins_
        res = mixins.component_mixin(base, mixins.BubbleDownMixin)
        assert not res
        assert len(base._mixins_) == 1

    def test_component_mixin_init(self):
        """
            Assert that the inits are run
        """
        base = self.base
        class TestMixin(object):
            def __init__(self):
                self.bob = 123
                num = getattr(self, 'num', 0)
                self.num = num + 1

        class TestMixin2(object):
            def __init__(self):
                self.frank = 22
                num = getattr(self, 'num', 0)
                self.num = num + 1

        mixins.component_mixin(base, TestMixin)
        mixins.component_mixin(base, TestMixin2)
        test = base()
        assert test.bob == 123
        assert test.num == 2
        assert test.frank == 22
        assert len(base._init_hooks) == 2
        # did not affect ancestor
        assert len(bc.PreMixComponent._init_hooks) == 0

    def test_component_mixin_listeners(self):
        """
        Assert that listeners
        """
        base = self.base
        class TestMixin(object):
            listeners = [(be.Event, 'handle_ev1')]
            def __init__(self):
                self.bob = 123
                num = getattr(self, 'num', 0)
                self.num = num + 1

            def handle_ev1(self, event):
                pass

        class TestMixin2(object):
            listeners = [(be.Event, 'handle_ev2')]
            def __init__(self):
                self.frank = 22
                num = getattr(self, 'num', 0)
                self.num = num + 1

            def handle_ev2(self, event):
                pass

        mixins.component_mixin(base, TestMixin)
        mixins.component_mixin(base, TestMixin2)
        test = base()
        assert len(test.listeners) == 2
        # did not affect ancestor
        assert len(bc.PreMixComponent.listeners) == 0

    def test_component_mixin_methods(self):
        """
        assert that methods are aggregated
        """
        base = self.base
        class TestMixin(object):
            def handle_ev1(self, event):
                pass

        class TestMixin2(object):
            def handle_ev2(self, event):
                pass

        mixins.component_mixin(base, TestMixin)
        mixins.component_mixin(base, TestMixin2)
        test = base()
        assert hasattr(test, 'handle_ev1')
        assert hasattr(test, 'handle_ev2')
        test.handle_ev1(None)
        test.handle_ev2(None)

    def test_component_mixin_methods_override(self):
        """
        assert that methods are aggregated
        """
        base = self.base
        class TestMixin(object):
            def dupe_method(self):
                return 1

        class TestMixin2(object):
            def dupe_method(self):
                return 2

        class TestMixin3(object):
            def dupe_method(self):
                return 3

        mixins.component_mixin(base, TestMixin)
        mixins.component_mixin(base, TestMixin2)
        test = base()
        # second one did not override first
        assert test.dupe_method() == 1

        # with override, third gets its method applied
        mixins.component_mixin(base, TestMixin3, override=['dupe_method'])
        assert test.dupe_method() == 3

    def test_component_mixin_add_component_hooks(self):
        """
        Allow Mixins to define cls_add_component_hooks
        """
        class TestBase(bc.PreMixComponent):
            pass
        base = TestBase
        class TestMixin(object):
            def mixin_add_component_hook(self, *args, **kwargs):
                self.mixin1 = True
                self.last_call = kwargs

        class TestMixin2(object):
            def mixin_add_component_hook(self, *args, **kwargs):
                self.mixin2 = True
                self.last_call2 = kwargs

        mixins.component_mixin(base, TestMixin)
        mixins.component_mixin(base, TestMixin2)
        test = base('parent')
        child = base('child')
        assert len(test.cls_add_component_hooks) == 2
        test.add_component(child, test_param=123)
        # make sure both ac hooks run
        assert test.last_call['test_param'] == 123
        assert test.last_call2['test_param'] == 123
        assert test.mixin1
        assert test.mixin2



if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-s','-x','--pdb', '--pdb-failure'],exit=False)   
