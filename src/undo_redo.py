# -*- coding: utf-8 -*-
# niño
# Copyright (c) 2016 Ross Anderson <ross.anderson@ualberta.ca>
# Copyright (c) 2020-2021 Mika Cousin <mika.cousin@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""Undo / Redo functionality for arbitrary classes."""


class EmptyCommandStackError(Exception):
    """Empty stack"""


class UndoManager:
    """Manages a stack of Command objects for the purpose of
    implementing undo/redo functionality.

    Usage:
        undo_mgr = UndoManager()
        undo_mgr.do(Command(params...))
        if undo_mgr.can_undo():
            undo_mgr.undo()
        if undo_mgr.can_redo():
            undo_mgr.redo()
    """

    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def do(self, command):
        """Execute command and manages undo / redo stacks.

        Args:
            command: Command

        Returns:
            command result
        """
        self._redo_stack.clear()
        self._undo_stack.append(command)
        return command.do()

    def can_undo(self):
        """Is undo possible ?

        Returns:
            True: Yes, False: No
        """
        return len(self._undo_stack) > 0

    def can_redo(self):
        """Is redo possible ?

        Returns:
            True: Yes, False: No
        """
        return len(self._redo_stack) > 0

    def undo(self):
        """Undo last command

        Raises:
            EmptyCommandStackError: Empty stack

        Returns:
            command result
        """
        if len(self._undo_stack) < 1:
            raise EmptyCommandStackError()
        command = self._undo_stack.pop()
        self._redo_stack.append(command)
        result = command.undo()
        func = getattr(command.obj, "undo", None)
        func()
        return result

    def redo(self):
        """Redo last undone command

        Raises:
            EmptyCommandStackError: Empty stack

        Returns:
            command result
        """
        if len(self._redo_stack) < 1:
            raise EmptyCommandStackError()
        command = self._redo_stack.pop()
        self._undo_stack.append(command)
        result = command.do()
        func = getattr(command.obj, "redo", None)
        func()
        return result


class Command:
    """A Command wraps a method call in an object which can do() and undo()."""

    def __init__(self, obj, do_method, *args):
        """Create a Command by passing an object, a method to call on the object,
        and a variable number of arguments to pass to the method.

        The object must support methods .copy() and .restore(obj).
        - copy() returns a copy of the object
        - restore(obj) restores the calling object to the state of the passed object

        These methods allow undo to work properly.

        Args:
            obj: object to call the method on
            do_method: method to call
            args: arguments to pass to the method
        """
        assert hasattr(obj, "copy")
        assert hasattr(obj, "restore")
        self.obj = obj
        self.do_method = do_method
        self.args = list(args)

        self.restore_point = None

    def do(self):
        """Set a restore point (copy the object), then call the method.

        Returns:
            obj.do_method(*args)
        """
        self.restore_point = self.obj.copy()
        return self.do_method(self.obj, *self.args)

    def undo(self):
        """Restore the object to the restore point created during do()

        Returns:
            obj.restore(restore_point)
        """
        return self.obj.restore(self.restore_point)


def undoable(func):
    """Decorator to allow an instance method to be undone.
    It does this by wrapping the method call as a Command,
    then calling self.do() on the command.
    Classes which use this decorator should implement a do() method like such:
        def do(self, command):
            return self.undo_manager.do(command)

    Args:
        func: method

    Returns:
        method
    """

    def wrapper(self, *args):
        return self.do(Command(self, func, *args))

    return wrapper
