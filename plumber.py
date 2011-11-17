#!/usr/bin/env python

import sys
import math

from gi.repository import Gtk

class Toolbar(Gtk.Toolbar):
    def __init__(self):
        super().__init__(toolbar_style=Gtk.ToolbarStyle.ICONS)

        self.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_SAVE))
        self.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_OPEN))
        self.add(Gtk.SeparatorToolItem())
        self.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_EDIT))
        self.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_DELETE))
        self.add(Gtk.SeparatorToolItem())
        self.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_UNDO))
        self.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_REDO))
        self.add(Gtk.SeparatorToolItem())
        self.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_MEDIA_PLAY))
        self.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_MEDIA_STOP))
        self.add(Gtk.SeparatorToolItem())
        self.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_HELP))

class ComponentPanes(Gtk.ToolPalette):
    def __init__(self):
        super().__init__(toolbar_style=Gtk.ToolbarStyle.BOTH)

        io_group = Gtk.ToolItemGroup(label='I/O')
        self.add(io_group)
        io_group.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD))

        search_group = Gtk.ToolItemGroup(label='Searching', collapsed=True)
        self.add(search_group)
        search_group.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD))

        sort_group = Gtk.ToolItemGroup(label='Sorting', collapsed=True)
        self.add(sort_group)
        sort_group.add(Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD))

class Canvas(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.connect('draw', self.do_draw)

    def do_draw(self, *args):
        if len(args) != 1:
            return

        ctx = args[0]
        width = self.get_allocated_width()
        height = self.get_allocated_height()

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

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(
                title='Plumber - Main Window',
                default_width=700,
                default_height=800,
        )

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(box)

        toolbar = Toolbar()
        box.add(toolbar)

        panes = Gtk.Paned(position=200)
        box.pack_end(panes, True, True, 0)

        components = ComponentPanes()
        panes.add1(components)

        canvas = Canvas()
        panes.add2(canvas)

        #button.connect('clicked', self.on_button_clicked)

def main(argv):
    window = MainWindow()
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
