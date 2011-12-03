import re

from gi.repository import Gtk

class FullPipeError(Exception): pass

class Component(object):
    def __init__(self):
        self.input_pipes = []
        self.output_pipes = []

    def attach_input(self, pipe):
        return self.attach(self.input_pipes, self.inputs, pipe)

    def attach_output(self, pipe):
        return self.attach(self.output_pipes, self.outputs, pipe)

    def attach(self, list, count, pipe):
        if len(list) >= count:
            raise FullPipeError()
        list.append(pipe)
        return list.index(pipe) + 1

    def detach_input(self, pipe):
        self.input_pipes.remove(pipe)

    def detach_output(self, pipe):
        self.output_pipes.remove(pipe)

    def init_properties(self, builder):
        pass

    def get_function(self, fname):
        return ''

class FileInputComponent(Component):
    name = 'File Input'
    category = 'I/O'
    inputs = 0
    outputs = 1

    properties_dialog = '''
        <interface>
            <object class="GtkBox" id="properties_box">
                <property name="orientation">vertical</property>
                <child>
                    <object class="GtkBox" id="box1">
                        <child><object class="GtkLabel" id="label1">
                            <property name="label">File Name:</property>
                        </object></child>
                        <child>
                            <object class="GtkFileChooserButton" id="filechooser1">
                                <property name="title">Input File Name</property>
                                <signal name="file-set" handler="set_input_file"/>
                            </object>
                            <packing>
                                <property name="expand">True</property>
                            </packing>
                        </child>
                    </object>
                </child>
            </object>
        </interface>'''

    def __init__(self):
        super(FileInputComponent, self).__init__()
        self.input_file = None

    def init_properties(self, builder):
        if self.input_file:
            file_chooser = builder.get_object('filechooser1')
            file_chooser.set_filename(self.input_file)

    def set_input_file(self, file_chooser):
        self.input_file = file_chooser.get_filename()

    def get_function(self, fname):
        return '''
function {} {{
    cat {} > $1
}}'''.format(fname, self.input_file)

class FileOutputComponent(Component):
    name = 'File Output'
    category = 'I/O'
    inputs = 1
    outputs = 0

    properties_dialog = '''
        <interface>
            <object class="GtkBox" id="properties_box">
                <property name="orientation">vertical</property>
                <child>
                    <object class="GtkBox" id="box1">
                        <child><object class="GtkLabel" id="label1">
                            <property name="label">File Name:</property>
                        </object></child>
                        <child>
                            <object class="GtkFileChooserButton" id="filechooser1">
                                <property name="title">Output File Name</property>
                                <signal name="file-set" handler="set_output_file"/>
                            </object>
                            <packing>
                                <property name="expand">True</property>
                            </packing>
                        </child>
                    </object>
                </child>
            </object>
        </interface>'''

    def __init__(self):
        super(FileOutputComponent, self).__init__()
        self.output_file = None

    def init_properties(self, builder):
        file_chooser = builder.get_object('filechooser1')
        if self.output_file:
            file_chooser.set_filename(self.output_file)

    def set_output_file(self, file_chooser):
        self.output_file = file_chooser.get_filename()

    def get_function(self, fname):
        return '''
function {} {{
    cat $1 > {}
}}'''.format(fname, self.output_file)

class FilterComponent(Component):
    name = 'Filter'
    category = 'Searching'
    inputs = 1
    outputs = 1

    properties_dialog = '''
        <interface>
            <object class="GtkBox" id="properties_box">
                <property name="orientation">vertical</property>
                <child>
                    <object class="GtkBox" id="box1">
                        <child><object class="GtkLabel" id="label1">
                            <property name="label">Regular Expression</property>
                        </object></child>
                        <child>
                            <object class="GtkEntry" id="entry1">
                                <signal name="changed" handler="set_regex"/>
                            </object>
                            <packing>
                                <property name="expand">True</property>
                            </packing>
                        </child>
                    </object>
                </child>
            </object>
        </interface>'''

    def __init__(self):
        super(FilterComponent, self).__init__()
        self.regex = None

    def init_properties(self, builder):
        entry = builder.get_object('entry1')
        if self.regex:
            entry.set_text(self.regex.pattern)

    def set_regex(self, entry):
        try:
            self.regex = re.compile(entry.get_text())
        except re.error:
            pass

    def get_function(self, fname):
        return '''
function {} {{
    grep -Pe \'{}\' $1 > $2
}}'''.format(fname, self.regex.pattern)

class SplitComponent(Component):
    name = 'Split'
    category = 'Editing'
    inputs = 1
    outputs = 2

    properties_dialog = '''
        <interface>
            <object class="GtkBox" id="properties_box">
                <property name="orientation">vertical</property>
                <child>
                    <object class="GtkBox" id="box1">
                        <child><object class="GtkLabel" id="label1">
                            <property name="label">Delimiter</property>
                        </object></child>
                        <child>
                            <object class="GtkEntry" id="entry1">
                                <signal name="changed" handler="set_delim"/>
                            </object>
                            <packing>
                                <property name="expand">True</property>
                            </packing>
                        </child>
                    </object>
                </child>
            </object>
        </interface>'''

    def __init__(self):
        super(SplitComponent, self).__init__()
        self.delim = None

    def init_properties(self, builder):
        entry = builder.get_object('entry1')
        if self.delim:
            entry.set_text(self.delim)

    def set_delim(self, entry):
        self.delim = entry.get_text()

    def get_function(self, fname):
        return '''
function {fname} {{
    while read line; do
        echo $line | awk -F \'{delim}\' \'{{print $1}}\'
        echo $line | awk -F \'{delim}\' \'{{print $2}}\' >&2
    done < $1 > $2 2> $3
}}'''.format(fname=fname, delim=self.delim)

class AddComponent(Component):
    name = 'Add'
    category = 'Calculations'
    inputs = 2
    outputs = 1

    properties_dialog = None

    def get_function(self, fname):
        return '''
function {} {{
    while read x <&3; do
        read y <&4
        echo $x + $y | bc
    done 3< $1 4< $2 > $3
}}'''.format(fname)

ACTIVE_COMPONENTS = [
        FileInputComponent,
        FileOutputComponent,
        FilterComponent,
        SplitComponent,
        AddComponent,
]
