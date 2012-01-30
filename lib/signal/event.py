#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       Event.py
#
#       Copyright 2012 Reid McKenzie <rmckenzie92@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#

from .signal import Signal

class Event(Signal):
    """
    events serve to signal things like damage being dealt, spells cast,
    effects resolving, land tapped, cards drawn etc.
    """
    def __init__(self, source):
        Signal.__init__(self, source)

class Draw(Event):
    cards   = None
    """
    This class serves to signal a player drawing cards.
    cards is the number of cards drawn.
    """
    def __init__(self, player, cards):
        Event.__init__(self, player)
        self.cards = cards

class Discard(Event):
    cards   = None
    """
    This class serves to signal a player discarding cards.
    cards is the number of cards discarded.
    """
    def __init__(self, player, cards):
        Event.__init__(self, player)
        self.cards = cards

class Exile(Event):
    target  = None
    """
    Signals a permanent's removal from the game by exiling.
    Target is the exiled card.
    Source is the card causing the exiling.
    """
    def __init__(self, source, target):
        Event.__init__(self, source)
        self.source = source

class Destroy(Event):
    target  = None
    """
    Signals the destruction of an artifact or permanent. This signal
    exists because some abilities (DarkSteel) can resist or handle its
    effects.
    Target is the permanent to be destroyed
    Source is the card/ability doing the destruction
    """
    def __init__(self, source, target):
        Event.__init__(self, source)
        self.source = source

class Cast(Event):
    target  = None
    spell   = None
    """
    This class serves to signal the casting of a generic spell. This is
    really just a base class for specific signals representing spells,
    instants, abilities and split seconds.
    Target is the target of the spell
    spell  is the instance of the spell being applied
    """
    def __init__(self, source, target, spell):
        Event.__init__(self, source)
        self.target = target
        self.spell  = spell

class Instant(Cast):
    """
    Special case of a castable which can happen at any time
    """
    def __init__(self, source, target, spell):
        cast.__init__(self, source, target, spell)

class Ability(Instant):
    """
    Special case of an instant which originates from a creature or artifact
    """
    def __init__(self, source, target, spell):
        Instant.__init__(self, source, target, spell)


class Spell(Cast):
    """
    Special case of a cast which has a "normal" (non-interrupt) priority
    TODO/NOTE - may need to note the controlling/source/curr_turn player
    """
    def __init__(self, source, target, spell):
        Cast.__init__(self, source, target, spell)

class Creature(Spell):
    """
    Special case of a spell which will result in the placement of a creature
    """
    def __init__(self, source, target, spell):
        Spell.__init__(self, source, target, spell)

class Artifact(Spell):
    """
    Special case of a spell which will result in the placement of an artifact
    """
    def __init__(self, source, target, spell):
        Spell.__init__(self, source, target, spell)