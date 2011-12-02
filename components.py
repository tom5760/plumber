class Component():
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
                            <object class="GtkFileChooserButton" id="button1">
                                <property name="title">Input File Name</property>
                            </object>
                            <packing>
                                <property name="expand">True</property>
                            </packing>
                        </child>
                    </object>
                </child>
            </object>
        </interface>'''

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
                            <object class="GtkFileChooserButton" id="button1">
                                <property name="title">Output File Name</property>
                            </object>
                            <packing>
                                <property name="expand">True</property>
                            </packing>
                        </child>
                    </object>
                </child>
            </object>
        </interface>'''

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
                            <object class="GtkEntry" id="entry" />
                            <packing>
                                <property name="expand">True</property>
                            </packing>
                        </child>
                    </object>
                </child>
            </object>
        </interface>'''

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
                            <property name="label">Regular Expression</property>
                        </object></child>
                        <child>
                            <object class="GtkEntry" id="entry" />
                            <packing>
                                <property name="expand">True</property>
                            </packing>
                        </child>
                    </object>
                </child>
            </object>
        </interface>'''

class AddComponent(Component):
    name = 'Add'
    category = 'Calculations'
    inputs = 2
    outputs = 1

    properties_dialog = None

ACTIVE_COMPONENTS = [
        FileInputComponent,
        FileOutputComponent,
        FilterComponent,
        SplitComponent,
        AddComponent,
]
