#!/usr/bin/env python

import sys
import math

from gi.repository import Gtk, Gdk, GObject

UI_FILE = 'gui.xml'
ID_MAIN_WINDOW = 'main_window'
ID_TOOLBAR_BUTTON = 'toolbar_'
ID_COMPONENT_PALETTE = 'component_palette'
ID_CANVAS = 'canvas'

GRID_SPACING = 30
GRID_LENGTH = 3
GRID_WIDTH = 0.1

class PlumberPart(object):
    def __init__(self, builder, components):
        self.builder = builder
        self.components = components

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

class ComponentDrawer(Gtk.DrawingArea):
    ICON_WIDTH = 50
    ICON_HEIGHT = 50

    CANVAS_WIDTH = 150
    CANVAS_HEIGHT = 75

    BASE_MARGIN = 5
    BASE_CORNER_RADIUS = 4
    BASE_LINE_WIDTH = 2
    BASE_STROKE_COLOR = (0, 0, 0)
    BASE_FILL_COLOR = (0, 191, 255)

    PORT_RADIUS = 4
    PORT_LINE_WIDTH = 1
    PORT_STROKE_COLOR = (0, 0, 0)
    PORT_IN_COLOR = (34, 139, 34)
    PORT_OUT_COLOR = (255, 140, 0)

    def __init__(self, component, is_icon):
        super().__init__()
        self.component = component
        self.is_icon = is_icon
        self.is_active = False

        self.connect('draw', self.do_draw)

        if self.is_icon:
            self.set_size_request(self.ICON_WIDTH, self.ICON_HEIGHT)
        else:
            self.set_can_focus(True)
            self.set_size_request(self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
            self.add_events(Gdk.EventMask.POINTER_MOTION_HINT_MASK
                            | Gdk.EventMask.BUTTON_MOTION_MASK
                            | Gdk.EventMask.BUTTON_PRESS_MASK
                            | Gdk.EventMask.BUTTON_RELEASE_MASK)

            self.connect('button-press-event', self.do_press)
            self.connect('button-release-event', self.do_release)

    def do_press(self, component, event):
        self.is_active = True
        self.grab_focus()

    def do_release(self, component, event):
        self.is_active = False

    def do_draw(self, *args):
        if len(args) == 1:
            ctx = args[0]
        else:
            ctx = args[1]

        width = self.get_allocated_width()
        height = self.get_allocated_height()
        self.draw_component(ctx, width, height)

    def draw_component(self, ctx, width, height):
        self.draw_base(ctx, width, height)
        self.draw_inputs(ctx, width, height)
        self.draw_outputs(ctx, width, height)

    @classmethod
    def draw_base(cls, ctx, width, height):
        x1 = y1 = cls.BASE_MARGIN
        x2 = width - cls.BASE_MARGIN
        y2 = height - cls.BASE_MARGIN
        r = cls.BASE_CORNER_RADIUS

        # From http://cairographics.org/cookbook/roundedrectangles Method D
        ctx.arc(x1 + r, y1 + r, r, 2 * (math.pi / 2), 3 * (math.pi / 2))
        ctx.arc(x2 - r, y1 + r, r, 3 * (math.pi / 2), 4 * (math.pi / 2))
        ctx.arc(x2 - r, y2 - r, r, 0, math.pi / 2)
        ctx.arc(x1 + r, y2 - r, r, math.pi / 2, 2 * (math.pi / 2))
        ctx.close_path()

        ctx.set_line_width(cls.BASE_LINE_WIDTH)
        ctx.set_source_rgb(*cls.BASE_STROKE_COLOR)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*cls.BASE_FILL_COLOR)
        ctx.fill()

    def draw_inputs(self, ctx, width, height):
        if self.component.inputs == 0:
            return

        self.draw_ports(ctx, width, height, self.BASE_MARGIN,
                        self.component.inputs)

    def draw_outputs(self, ctx, width, height):
        if self.component.outputs == 0:
            return

        self.draw_ports(ctx, width, height, width - self.BASE_MARGIN,
                        self.component.outputs)

    @classmethod
    def draw_ports(cls, ctx, width, height, x, count):
        available_space = (height - cls.BASE_MARGIN * 2)
        offset = available_space / (count + 1)

        y = cls.BASE_MARGIN + offset

        ctx.set_line_width(cls.PORT_LINE_WIDTH)
        for c in range(count):
            ctx.arc(x, y, cls.PORT_RADIUS, 0, 360)
            ctx.set_source_rgb(0, 0, 0)
            ctx.close_path()
            ctx.stroke_preserve()
            ctx.set_source_rgb(255, 0, 0)
            ctx.fill()
            y += offset

class FileInputComponent(object):
    name = 'File Input'
    category = 'I/O'
    inputs = 0
    outputs = 1

class FileOutputComponent(object):
    name = 'File Output'
    category = 'I/O'
    inputs = 1
    outputs = 0

class FilterComponent(object):
    name = 'Filter'
    category = 'Searching'
    inputs = 1
    outputs = 1

class SplitComponent(object):
    name = 'Split'
    category = 'Editing'
    inputs = 1
    outputs = 2

class ComponentPalette(PlumberPart):
    def init_ui(self):
        self.categories = {}
        pane = self.builder.get_object(ID_COMPONENT_PALETTE)

        for component in self.components.values():
            button = Gtk.ToolButton.new(None, component.name)
            button.set_icon_widget(ComponentDrawer(component, True))
            button.set_use_drag_window(True)
            button.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, None, Gdk.DragAction.COPY)
            button.drag_source_add_text_targets()

            #button.connect('drag-begin', self.do_drag_begin, component.name)
            button.connect('drag-data-get', self.do_data_get, component.name)

            try:
                group = self.categories[component.category]
            except KeyError:
                group = Gtk.ToolItemGroup(label=component.category)
                self.categories[component.category] = group
                pane.add(group)

            group.add(button)

    #def do_drag_begin(self, button, drag_context, name):
    #    print('drag', name, button)
    #    #button.drag_source_set_icon_pixbuf(buf)

    def do_data_get(self, button, context, data, info, time, name):
        data.set_text(name, len(name))

class Canvas(PlumberPart):
    COMPONENT_WIDTH = 150
    COMPONENT_HEIGHT = 75

    def init_ui(self):
        canvas = self.builder.get_object(ID_CANVAS)
        canvas.add_events(Gdk.EventMask.POINTER_MOTION_HINT_MASK
                          | Gdk.EventMask.BUTTON_MOTION_MASK
                          | Gdk.EventMask.BUTTON_PRESS_MASK
                          | Gdk.EventMask.BUTTON_RELEASE_MASK)

        canvas.set_reallocate_redraws(True)

        #canvas.put(ComponentDrawer(SplitComponent(), False), 300, 300)

        #canvas.drag_dest_set(Gtk.DestDefaults.MOTION | Gtk.DestDefaults.DROP,
        canvas.drag_dest_set(Gtk.DestDefaults.MOTION | Gtk.DestDefaults.DROP,
                             None, Gdk.DragAction.COPY)
        canvas.drag_dest_add_text_targets()

        canvas.connect('draw', self.do_draw)
        canvas.connect('motion-notify-event', self.do_click)
        #canvas.connect('drag-motion', self.do_drag_motion)
        #canvas.connect('drag-drop', self.do_drag_drop)
        canvas.connect('drag-data-received', self.do_drag_received)

    def do_click(self, canvas, event):
        component = canvas.get_focus_child()
        if not component or not component.is_active:
            return

        value = GObject.Value()
        value.init(GObject.TYPE_INT)

        canvas.child_get_property(component, 'x', value)
        value.set_int(value.get_int() + event.x - self.COMPONENT_WIDTH / 2)
        canvas.child_set_property(component, 'x', value)

        canvas.child_get_property(component, 'y', value)
        value.set_int(value.get_int() + event.y - self.COMPONENT_HEIGHT / 2)
        canvas.child_set_property(component, 'y', value)

    #def do_drag_motion(self, canvas, context, x, y, time):
    #    print('drag motion ({}, {}) at {}'.format(x, y, time))
    #    return True

    #def do_drag_drop(self, canvas, context, x, y, time):
    #    print('drag drop ({}, {}) at {}'.format(x, y, time))
    #    canvas.drag_get_data(context, Gdk.Atom.intern('foo', False), time)
    #    return True

    def do_drag_received(self, canvas, context, x, y, data, info, time):
        component = self.components[data.get_text()]
        Gtk.drag_finish(context, True, False, time)

        drawer = ComponentDrawer(component(), False)
        drawer.set_visible(True)
        canvas.put(drawer,
                   x - self.COMPONENT_WIDTH / 2,
                   y - self.COMPONENT_HEIGHT / 2)

        canvas.get_window().invalidate_rect(None, True)

    def do_draw(self, canvas, ctx):
        width = canvas.get_allocated_width()
        height = canvas.get_allocated_height()

        self.draw_background(ctx, width, height)
        self.draw_grid(ctx, width, height)

        value = GObject.Value()
        value.init(GObject.TYPE_INT)

    def draw_background(self, ctx, width, height):
        ctx.save()
        ctx.set_source_rgb(255, 255, 255)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
        ctx.restore()

    def draw_grid(self, ctx, width, height):
        ctx.save()
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
        ctx.restore()

    def draw_components(self, ctx, width, height):
        for component in self.components:
            x, y = component.position
            x1 = x - self.COMPONENT_WIDTH / 2
            y1 = y - self.COMPONENT_HEIGHT / 2
            ctx.rectangle(x1, y1, self.COMPONENT_WIDTH, self.COMPONENT_HEIGHT)
            ctx.save()
            ctx.clip()
            ctx.translate(x1, y1)

            component.draw(ctx, self.COMPONENT_WIDTH, self.COMPONENT_HEIGHT)

            ctx.restore()

    #def draw_spiral(self, ctx, width, height):
    #    wd = .02 * width
    #    hd = .02 * height

    #    width -= 2
    #    height -= 2

    #    ctx.move_to (width + 1, 1-hd)
    #    for i in range(9):
    #        ctx.rel_line_to (0, height - hd * (2 * i - 1))
    #        ctx.rel_line_to (- (width - wd * (2 *i)), 0)
    #        ctx.rel_line_to (0, - (height - hd * (2*i)))
    #        ctx.rel_line_to (width - wd * (2 * i + 1), 0)

    #    ctx.set_source_rgb (0, 0, 1)
    #    ctx.stroke()

    #def draw_dot(self, ctx, width, height):
    #    ctx.arc(self.dot[0], self.dot[1], 10, 0, 360)
    #    ctx.set_source_rgb(0, 0, 0)
    #    ctx.fill()

class Plumber(object):
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)

        self.components = {}
        for c in (FileInputComponent, FilterComponent,
                  FileOutputComponent, SplitComponent):
            self.components[c.name] = c

        self.init_ui()

    def start(self):
        self.builder.get_object(ID_MAIN_WINDOW).show_all()

    def init_ui(self):
        'Wires the UI XML description to the actual implementing code.'
        main_window = self.builder.get_object(ID_MAIN_WINDOW)
        main_window.connect('destroy', Gtk.main_quit)

        Toolbar(self.builder, self.components).init_ui()
        ComponentPalette(self.builder, self.components).init_ui()
        Canvas(self.builder, self.components).init_ui()

def main(argv):
    p = Plumber()
    p.start()
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
