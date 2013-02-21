"""
    The purpose of this Test Module is to test/document the event handling of Components

    Terms:
        super parent : Parent Component that has no parents. Normally a BounceBox.
        sub component : A component that is parent.add_component(comp) to a parent
        cousins : Components are the sub-components of the same parent. 
"""
from unittest import TestCase

from mock import MagicMock

import bouncebox.core.component as bc
import bouncebox.core.box as bbox
import bouncebox.core.event as be
import bouncebox.middleware as middleware

def test_subscribe():
    """
    The pub/sub framework consists of two functions: 
        subscribe(self, callback, event_cls=None)
        publish(self, event)

    Subscribing to a publishers event can be done like so:

    >> pub.subscribe(sub.callaback, event_type)
    >> pub.broadcast(event)
         
    Note that broadcast calls publish. Publish itself should not be called directly
    Outside of this, there is no other connection from sub/pub. They do not have to be in the same box, component,
    or even connected at all
    """
    pub = bc.Component()
    sub = bc.Component()
    sub.event_handler = MagicMock()
    pub.subscribe(sub.event_handler)

    # Test publish function
    evt = be.Event()
    pub.publish(evt)
    sub.event_handler.assert_called_once_with(evt)

    # broadcast calls publish
    evt2 = be.Event()
    pub.broadcast(evt2)
    sub.event_handler.assert_called_with(evt2)

def test_add_component_super_parent():
    """
    Adding a component to a super parent Component(not a bouncebox)

    This will act pretty much like the super parent is a BounceBox

    child.broadcast will send events to the parent.router.
    Other components that were added with add_component will listen to the same router.

                        Router        Audience                    
    child.broadcast     Parent      cousins(parent.router)      
    parent.broadcast    self        sub components              

                        Router
    child.listeners     parent.router
    """
    parent = bc.Component()
    source = bc.Component()
    comp = bc.Component()
    comp.handler = MagicMock()
    comp.add_event_listener(be.Event, comp.handler)

    parent.add_component(comp)
    parent.add_component(source)
    parent.router.start_logging()
    evt = be.Event()

    source.broadcast(evt)
    assert parent.router.logs[0] is evt
    # other comp
    comp.handler.assert_called_once_with(evt)

    evt2 = be.Event()
    parent.broadcast(evt2)
    # super parent is own front
    assert parent.front is parent
    # parent.broadcast goes to its own router
    print parent.router.logs[1] is evt2

def test_add_component_box():
    """
    Adding a component to a Component that is inside a box

    02-21-13
    Changed this so child component broadcasts to parent.router. This acts
    as if contained is always True

                        Router       Audience                
    child.broadcast     parent      siblings(parent.router)   
    parent.broadcast    front(box)  cousins(front.router)
    box.broadcast       self        all components connected to its router

                        Router
    child.listeners     parent.router # Which means it normamly won't be called.

    # NOTE: It is conceivable that we should propogate the child listeners to front.
    But for now, we're leaving it. We will address this by creating different 
    capabilities like Middleware
    """
    box = bbox.BounceBox()
    parent = bc.Component()
    source = bc.Component()
    comp = bc.Component()
    comp.handler = MagicMock()
    comp.add_event_listener(be.Event, comp.handler)
    box_child = bc.Component()
    box_child.handler = MagicMock()
    box_child.add_event_listener(be.Event, box_child.handler)

    box.add_component(parent)
    box.add_component(box_child)
    parent.add_component(comp)
    parent.add_component(source)
    # router logging
    parent.router.start_logging()
    box.router.start_logging()

    evt = be.Event()

    # a grandchild broadcasting will go to the front.router
    source.broadcast(evt)
    assert parent.router.logs[0] is evt
    assert len(box.router.logs) == 0

    # sibling gets called
    comp.handler.assert_called_once_with(evt)
    # since parent.router is used. box_child should not be called
    assert box_child.handler.call_count == 0

    evt2 = be.Event()
    parent.broadcast(evt2)
    assert parent.front is box
    assert box.router.logs[0] is evt2

def test_middleware():
    """"
    Middleware has the concept of children instead of component. 

    The Middleware has an event_handler that accepts all Events, it passes this event
    to its down_router, which then propogates events to children. 

    child broadcasts are sent to handle_bubble_up, which then broadcasts the event to
    the router. 

    In essense, the middleware acts just like 


                            Router              Audience                
    child.broadcast         parent(relayed     siblings (since mid will bubble_down)
                            to front)          + cousins(direct children of front) 

    mid.broadcast           front(box)          cousins(parent.router) 
                                                + children(it will bubble down)
    box.broadcast           self                all components connected to its router

                            Router
    child.listeners         parent.down_router(relayed)
    """
    box = bbox.BounceBox()
    mid = middleware.Middleware()
    source = bc.Component()
    comp = bc.Component()
    comp.handler = MagicMock()
    comp.add_event_listener(be.Event, comp.handler)
    box_child = bc.Component()
    box_child.handler = MagicMock()
    box_child.add_event_listener(be.Event, box_child.handler)
    mid.handler = MagicMock()
    mid.add_event_listener(be.Event, mid.handler)

    # router logging
    box.router.start_logging()

    box.add_component(mid)
    box.add_component(box_child)
    mid.add_child(comp)
    mid.add_child(source)

    evt = be.Event()
    source.broadcast(evt)
    # will bubble up to box.router
    assert box.router.logs[0] == evt
    # sibling gets event due to front -> mid -> bubbledown -> sibling
    comp.handler.assert_called_once_with(evt)
    # direct box children get event
    box_child.handler.assert_called_once_with(evt)

    evt2 = be.Event()
    mid.broadcast(evt2)
    # hits front box
    assert box.router.logs[1] == evt2
    # no different than child broadcasting. bubbles down
    comp.handler.assert_called_with(evt2)
    box_child.handler.assert_called_with(evt2)

def test_combo():
    """
    Room for future test. I want an add_child/component where I can mix and match whether the child
    gains access to outside events via the bubble_down. And where the parent can up bubble only selected events. 
                            Router              Audience                
    child.broadcast         parent              parent.router siblings

    mid.broadcast           front(box)          front(box) 
    mid.bubble_down         down_router         children
    box.broadcast           self                all components connected to its router

                            Router
    child.listeners         parent.down_router(relayed)
    """


if __name__ == '__main__':
    import nose                                                                      
    nose.runmodule(argv=[__file__,'-s','-x','--pdb', '--pdb-failure'],exit=False)   
