#!/usr/bin/env python

import sys
import math

from gi.repository import Gtk, Gdk

UI_FILE = 'gui.xml'
ID_MAIN_WINDOW = 'main_window'
ID_TOOLBAR_BUTTON = 'toolbar_'
ID_CANVAS = 'canvas'

GRID_SPACING = 30
GRID_LENGTH = 3
GRID_WIDTH = 0.1

class PlumberPart(object):
    def __init__(self, builder):
        self.builder = builder

    # This class needs to be subclassed
    def init_ui(self):
        raise NotImplementedError('Implement this!')

class Toolbar(PlumberPart):
    BUTTONS = ('save', 'open', 'edit', 'delete', 'undo', 'redo', 'play',
               'stop', 'help',)

    def init_ui(self):
        for name in Toolbar.BUTTONS:
            button = self.builder.get_object(ID_TOOLBAR_BUTTON + name)
            button.connect('clicked', getattr(self, 'do_' + name))

    def do_save(self, button):
        print('SAVE')

    def do_open(self, button):
        print('OPEN')

    def do_edit(self, button):
        print('EDIT')

    def do_delete(self, button):
        print('DELETE')

    def do_undo(self, button):
        print('UNDO')

    def do_redo(self, button):
        print('REDO')

    def do_play(self, button):
        print('PLAY')

    def do_stop(self, button):
        print('STOP')

    def do_help(self, button):
        print('HELP')

class ComponentPanes(PlumberPart):
    def init_ui(self):
        pass

class Canvas(PlumberPart):
    def init_ui(self):
        canvas = self.builder.get_object(ID_CANVAS)
        canvas.add_events(Gdk.EventMask.POINTER_MOTION_HINT_MASK
                          | Gdk.EventMask.BUTTON_MOTION_MASK
                          | Gdk.EventMask.BUTTON_PRESS_MASK
                          | Gdk.EventMask.BUTTON_RELEASE_MASK)
        canvas.connect('draw', self.do_draw)
        canvas.connect('button-press-event', self.do_click)
        canvas.connect('motion-notify-event', self.do_click)

        self.dot = (0, 0)

    def do_click(self, drawing, event):
        self.dot = (int(event.x), int(event.y))
        drawing.get_window().invalidate_rect(None, True)

    def do_draw(self, drawing, ctx):
        width = drawing.get_allocated_width()
        height = drawing.get_allocated_height()

        self.draw_background(ctx, width, height)
        self.draw_grid(ctx, width, height)
        self.draw_dot(ctx, width, height)

    def draw_background(self, ctx, width, height):
        ctx.set_source_rgb(255, 255, 255)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

    def draw_grid(self, ctx, width, height):
        ctx.set_line_width(GRID_WIDTH)
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_dash((GRID_LENGTH,))

        for x in range(0, width, GRID_SPACING):
            ctx.move_to(x, 0)
            ctx.line_to(x, height)

        for y in range(0, height, GRID_SPACING):
            ctx.move_to(0, y)
            ctx.line_to(width, y)
        ctx.stroke()

    def draw_spiral(self, ctx, width, height):
        wd = .02 * width
        hd = .02 * height

        width -= 2
        height -= 2

        ctx.move_to (width + 1, 1-hd)
        for i in range(9):
            ctx.rel_line_to (0, height - hd * (2 * i - 1))
            ctx.rel_line_to (- (width - wd * (2 *i)), 0)
            ctx.rel_line_to (0, - (height - hd * (2*i)))
            ctx.rel_line_to (width - wd * (2 * i + 1), 0)

        ctx.set_source_rgb (0, 0, 1)
        ctx.stroke()

    def draw_dot(self, ctx, width, height):
        ctx.arc(self.dot[0], self.dot[1], 10, 0, 360)
        ctx.set_source_rgb(0, 0, 0)
        ctx.fill()

class Plumber(object):
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)

        self.init_ui()

    def start(self):
        self.builder.get_object(ID_MAIN_WINDOW).show_all()

    def init_ui(self):
        'Wires the UI XML description to the actual implementing code.'
        main_window = self.builder.get_object(ID_MAIN_WINDOW)
        main_window.connect('destroy', Gtk.main_quit)

        Toolbar(self.builder).init_ui()
        ComponentPanes(self.builder).init_ui()
        Canvas(self.builder).init_ui()

def main(argv):
    p = Plumber()
    p.start()
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
