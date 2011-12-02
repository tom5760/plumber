#!/usr/bin/env python

import sys
import math

from gi.repository import Gtk, Gdk

UI_FILE = 'gui.xml'
ID_MAIN_WINDOW = 'main_window'
ID_TOOLBAR_BUTTON = 'toolbar_'
ID_COMPONENT_PALETTE = 'component_palette'
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

class FileInputComponent(object):
    name = 'File Input'
    category = 'I/O'

class FileOutputComponent(object):
    name = 'File Output'
    category = 'I/O'

class FilterComponent(object):
    name = 'Filter'
    category = 'Searching'

class ComponentPalette(PlumberPart):
    def __init__(self, builder):
        super().__init__(builder)

        self.categories = {}
        self.components = {}

        for c in (FileInputComponent(), FilterComponent(),
                  FileOutputComponent()):
            self.components[c.name] = c

    def init_ui(self):
        pane = self.builder.get_object(ID_COMPONENT_PALETTE)

        for component in self.components.values():
            button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
            button.set_label(component.name)
            button.set_use_drag_window(True)
            button.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, None, Gdk.DragAction.COPY)
            button.drag_source_add_text_targets()
            button.connect('drag-begin', self.do_drag_begin, component.name)
            button.connect('drag-data-get', self.do_data_get, component.name)

            try:
                group = self.categories[component.category]
            except KeyError:
                group = Gtk.ToolItemGroup(label=component.category)
                self.categories[component.category] = group
                pane.add(group)

            group.add(button)

    def do_drag_begin(self, button, drag_context, name):
        print('drag', name)

    def do_data_get(self, button, context, data, info, time, name):
        data.set_text(name, len(name))
        print('component drag data', name)

class Canvas(PlumberPart):
    def init_ui(self):
        canvas = self.builder.get_object(ID_CANVAS)

        canvas.add_events(Gdk.EventMask.POINTER_MOTION_HINT_MASK
                          | Gdk.EventMask.BUTTON_MOTION_MASK
                          | Gdk.EventMask.BUTTON_PRESS_MASK
                          | Gdk.EventMask.BUTTON_RELEASE_MASK)

        #canvas.drag_dest_set(Gtk.DestDefaults.MOTION | Gtk.DestDefaults.DROP,
        canvas.drag_dest_set(Gtk.DestDefaults.ALL, None, Gdk.DragAction.COPY)
        canvas.drag_dest_add_text_targets()

        canvas.connect('draw', self.do_draw)
        canvas.connect('button-press-event', self.do_click)
        canvas.connect('motion-notify-event', self.do_click)
        #canvas.connect('drag-motion', self.do_drag_motion)
        #canvas.connect('drag-drop', self.do_drag_drop)
        canvas.connect('drag-data-received', self.do_drag_received)

        self.dot = (0, 0)

    def do_click(self, canvas, event):
        self.dot = (int(event.x), int(event.y))
        canvas.get_window().invalidate_rect(None, True)

    #def do_drag_motion(self, canvas, context, x, y, time):
    #    print('drag motion ({}, {}) at {}'.format(x, y, time))
    #    return True

    #def do_drag_drop(self, canvas, context, x, y, time):
    #    print('drag drop ({}, {}) at {}'.format(x, y, time))
    #    canvas.drag_get_data(context, Gdk.Atom.intern('foo', False), time)
    #    return True

    def do_drag_received(self, canvas, context, x, y, data, info, time):
        print('drag data received ({}, {}) at {} with {}'.format(x, y, time, data.get_text()))
        Gtk.drag_finish(context, True, False, time)

    def do_draw(self, canvas, ctx):
        width = canvas.get_allocated_width()
        height = canvas.get_allocated_height()

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
        ComponentPalette(self.builder).init_ui()
        Canvas(self.builder).init_ui()

def main(argv):
    p = Plumber()
    p.start()
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
