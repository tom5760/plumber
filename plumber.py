#!/usr/bin/env python

import sys
import math

import cairo
from gi.repository import Gtk, Gdk, GObject

import components

UI_FILE = 'gui.xml'
ID_MAIN_WINDOW = 'main_window'
ID_TOOLBAR_BUTTON = 'toolbar_'
ID_COMPONENT_PALETTE = 'component_palette'
ID_CANVAS = 'canvas'

class FullPipeError(Exception): pass

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

    CANVAS_WIDTH = 125
    CANVAS_HEIGHT = 55

    FONT_FACE = 'Sans'
    FONT_SIZE = 15

    BASE_MARGIN = 5
    BASE_CORNER_RADIUS = 4
    BASE_LINE_WIDTH = 2
    BASE_STROKE_COLOR = (0, 0, 0)
    BASE_FILL_COLOR = (135 / 255, 206 / 255, 250 / 255, 0.1)
    BASE_FILL_COLOR_SELECTED = (255 / 255, 215 / 255, 0 / 255, 0.1)

    PORT_RADIUS = 4
    PORT_LINE_WIDTH = 1
    PORT_STROKE_COLOR = (0, 0, 0)
    PORT_IN_COLOR = (34 / 255, 139 / 255, 34 / 255)
    PORT_OUT_COLOR = (255 / 255, 140 / 255, 0 / 255)

    def __init__(self, builder, component, is_icon):
        super().__init__()
        self.builder = builder
        self.component = component
        self.is_icon = is_icon
        self.is_drag = False
        self.is_selected = False

        self.connect('draw', self.do_draw)

        #self.override_background_color(0, Gdk.RGBA(0, 0, 0, 0.1))

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
        self.get_parent().set_focus_child(self)
        if event.button == 1:
            self.is_drag = True
        if event.button == 3:
            self.is_selected = True
            self.get_window().invalidate_rect(None, True)

        if event.type == Gdk.EventType._2BUTTON_PRESS:
            if self.component.properties_dialog is None:
                return

            dialog = Gtk.Dialog(self.component.name + ' Properties',
                                self.builder.get_object(ID_MAIN_WINDOW),
                                Gtk.DialogFlags.MODAL
                                    | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                (Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

            dbuilder = Gtk.Builder()
            dbuilder.add_from_string(self.component.properties_dialog)

            content_area = dialog.get_content_area()
            content_area.pack_start(dbuilder.get_object('properties_box'),
                                    False, False, 0)
            content_area.show_all()

            response = dialog.run()
            print('Response:', response)
            dialog.destroy()

    def do_release(self, component, event):
        self.is_drag = False

    def do_draw(self, *args):
        if len(args) == 1:
            ctx = args[0]
        else:
            ctx = args[1]

        width = self.get_allocated_width()
        height = self.get_allocated_height()

        ctx.save()
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
        ctx.restore()

        self.draw_component(ctx, width, height)

    def draw_component(self, ctx, width, height):
        self.draw_base(ctx, width, height)
        self.draw_inputs(ctx, width, height)
        self.draw_outputs(ctx, width, height)
        if not self.is_icon:
            self.draw_name(ctx, width, height)

    def draw_base(self, ctx, width, height):
        x1 = y1 = self.BASE_MARGIN
        x2 = width - self.BASE_MARGIN
        y2 = height - self.BASE_MARGIN
        r = self.BASE_CORNER_RADIUS

        # From http://cairographics.org/cookbook/roundedrectangles Method D
        ctx.arc(x1 + r, y1 + r, r, 2 * (math.pi / 2), 3 * (math.pi / 2))
        ctx.arc(x2 - r, y1 + r, r, 3 * (math.pi / 2), 4 * (math.pi / 2))
        ctx.arc(x2 - r, y2 - r, r, 0, math.pi / 2)
        ctx.arc(x1 + r, y2 - r, r, math.pi / 2, 2 * (math.pi / 2))
        ctx.close_path()

        ctx.set_line_width(self.BASE_LINE_WIDTH)
        ctx.set_source_rgb(*self.BASE_STROKE_COLOR)
        ctx.stroke_preserve()
        if self.is_selected:
            ctx.set_source_rgba(*self.BASE_FILL_COLOR_SELECTED)
        else:
            ctx.set_source_rgba(*self.BASE_FILL_COLOR)
        ctx.fill()

    def draw_inputs(self, ctx, width, height):
        if self.component.inputs == 0:
            return

        self.draw_ports(ctx, width, height, self.BASE_MARGIN,
                        self.component.inputs, self.PORT_IN_COLOR)

    def draw_outputs(self, ctx, width, height):
        if self.component.outputs == 0:
            return

        self.draw_ports(ctx, width, height, width - self.BASE_MARGIN,
                        self.component.outputs, self.PORT_OUT_COLOR)

    @classmethod
    def draw_ports(cls, ctx, width, height, x, count, color):
        available_space = (height - cls.BASE_MARGIN * 2)
        offset = available_space / (count + 1)

        y = cls.BASE_MARGIN + offset

        ctx.set_line_width(cls.PORT_LINE_WIDTH)
        for c in range(count):
            ctx.arc(x, y, cls.PORT_RADIUS, 0, 360)
            ctx.set_source_rgb(0, 0, 0)
            ctx.close_path()
            ctx.stroke_preserve()
            ctx.set_source_rgb(*color)
            ctx.fill()
            y += offset

    def draw_name(self, ctx, width, height):
        ctx.select_font_face(self.FONT_FACE)
        ctx.set_font_size(self.FONT_SIZE)
        ctx.move_to(self.BASE_MARGIN * 4, height - self.BASE_MARGIN * 4)
        ctx.set_source_rgb(0, 0, 0)
        ctx.show_text(self.component.name)
        ctx.stroke()

class ComponentPalette(PlumberPart):
    def init_ui(self):
        self.categories = {}
        pane = self.builder.get_object(ID_COMPONENT_PALETTE)

        for component in self.components.values():
            button = Gtk.ToolButton.new(None, component.name)
            button.set_icon_widget(ComponentDrawer(self.builder, component,
                                                   True))
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

class CanvasPipe(object):
    PIPE_WIDTH = 6
    PIPE_COLOR = (0, 0, 0)

    def __init__(self, start, end):
        self.start = start
        self.end = end
        start.component.attach_output(self)
        end.component.attach_input(self)

    def detach(self):
        self.start.component.detach_output(self)
        self.end.component.detach_input(self)

    def do_draw(self, canvas, ctx):
        ctx.set_line_width(self.PIPE_WIDTH)
        ctx.set_source_rgb(*self.PIPE_COLOR)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)

        value = GObject.Value()
        value.init(GObject.TYPE_INT)

        height = (ComponentDrawer.CANVAS_HEIGHT - ComponentDrawer.BASE_MARGIN * 2)

        start_n = self.start.component.output_pipes.index(self) + 1
        end_n = self.end.component.input_pipes.index(self) + 1

        start_offset = height / (self.start.component.outputs + 1) * start_n
        end_offset = height / (self.end.component.inputs + 1) * end_n

        canvas.child_get_property(self.start, 'x', value)
        start_x = value.get_int() + ComponentDrawer.CANVAS_WIDTH
        canvas.child_get_property(self.start, 'y', value)
        start_y = value.get_int() + start_offset

        canvas.child_get_property(self.end, 'x', value)
        end_x = value.get_int() + ComponentDrawer.BASE_MARGIN
        canvas.child_get_property(self.end, 'y', value)
        end_y = value.get_int() + end_offset

        ctx.move_to(start_x, start_y)
        ctx.line_to(start_x + ((end_x - start_x) / 2), start_y)
        ctx.line_to(start_x + ((end_x - start_x) / 2), end_y)
        ctx.line_to(end_x, end_y)
        ctx.stroke()

class Canvas(PlumberPart):
    GRID_SPACING = 30
    GRID_LENGTH = 3
    GRID_WIDTH = 0.1

    def init_ui(self):
        self.pipes = []
        self.last_selected = None

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
        canvas.connect('motion-notify-event', self.do_motion)
        canvas.connect('button-release-event', self.do_release)
        #canvas.connect('drag-motion', self.do_drag_motion)
        #canvas.connect('drag-drop', self.do_drag_drop)
        canvas.connect('drag-data-received', self.do_drag_received)

    def do_release(self, canvas, event):
        component = canvas.get_focus_child()
        canvas.set_focus_child(None)

        if (component and component.is_selected
                and self.last_selected != component):
            if self.last_selected is None:
                self.last_selected = component
            else:
                pipe = self.find_pipe(self.last_selected, component)
                if pipe is not None:
                    pipe.detach()
                    self.pipes.remove(pipe)
                else:
                    try:
                        self.pipes.append(CanvasPipe(self.last_selected, component))
                    except FullPipeError:
                        pass
                self.deselect_children(canvas)

        canvas.get_window().invalidate_rect(None, True)

    def deselect_children(self, canvas):
        for child in canvas.get_children():
            child.is_selected = False
            child.get_window().invalidate_rect(None, True)
        self.last_selected = None

    def find_pipe(self, start, end):
        for pipe in self.pipes:
            if pipe.start is start and pipe.end is end:
                return pipe
        return None

    def do_motion(self, canvas, event):
        component = canvas.get_focus_child()
        if not component or not component.is_drag:
            return

        value = GObject.Value()
        value.init(GObject.TYPE_INT)

        canvas.child_get_property(component, 'x', value)
        value.set_int(value.get_int() + event.x
                      - ComponentDrawer.CANVAS_WIDTH / 2)
        canvas.child_set_property(component, 'x', value)

        canvas.child_get_property(component, 'y', value)
        value.set_int(value.get_int() + event.y
                      - ComponentDrawer.CANVAS_HEIGHT / 2)
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

        drawer = ComponentDrawer(self.builder, component(), False)
        drawer.set_visible(True)
        canvas.put(drawer,
                   x - ComponentDrawer.CANVAS_WIDTH / 2,
                   y - ComponentDrawer.CANVAS_HEIGHT/ 2)

        canvas.get_window().invalidate_rect(None, True)

    def do_draw(self, canvas, ctx):
        width = canvas.get_allocated_width()
        height = canvas.get_allocated_height()

        self.draw_background(ctx, width, height)
        self.draw_grid(ctx, width, height)

        for pipe in self.pipes:
            ctx.save()
            pipe.do_draw(canvas, ctx)
            ctx.restore()

    def draw_background(self, ctx, width, height):
        ctx.save()
        ctx.set_source_rgb(255, 255, 255)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
        ctx.restore()

    def draw_grid(self, ctx, width, height):
        ctx.save()
        ctx.set_line_width(self.GRID_WIDTH)
        ctx.set_source_rgb(0, 0, 0)
        ctx.set_dash((self.GRID_LENGTH,))

        for x in range(0, width, self.GRID_SPACING):
            ctx.move_to(x, 0)
            ctx.line_to(x, height)

        for y in range(0, height, self.GRID_SPACING):
            ctx.move_to(0, y)
            ctx.line_to(width, y)
        ctx.stroke()
        ctx.restore()

class Plumber(object):
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)

        self.components = {}
        for c in components.ACTIVE_COMPONENTS:
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
