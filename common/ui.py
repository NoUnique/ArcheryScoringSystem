import sys # to get function name from inside the function
import tkinter as Tk
from tkinter import font, messagebox
import xml.etree.ElementTree as ETree

# http://effbot.org/zone/element-tkinter.htm
# http://www.nohuddleoffense.de/2011/04/20/generating-tkinter-guis-from-xml/
# http://pydoc.net/Python/pytkgen/1.0/tkgen.gengui/

class AppFrame(Tk.Frame):
    def __init__(self, layout=None):

        # Initial values
        self.elements = {}
        self.variables = {}
        self.flag_terminate = None

        # Make Tkinter Frame
        self.root = Tk.Tk()
        self.root.resizable(0, 0) # Disable Resizability
        self.root.protocol('WM_DELETE_WINDOW', self.terminate)
        super().__init__(self.root)

        # Load XML file
        element = ETree.parse(layout).getroot()
        self._load_xml(self.root, element)
        self.frame.grid()

        print('')
        print(self.root.title())
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print('@@@@@@@@@ Initialize @@@@@@@@')
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print('')

    # Load UI layout from XML
    def _load_xml(self, master, element):
        if(element.tag == "Frame"):
            # remove element.attrib to write title on XML
            #self.frame = Tk.Frame(master, **element.attrib)
            self.frame = Tk.Frame(master)

            master.title(element.attrib['version'])
            for subelement in element:
                widget, grid_info = self._load_xml(self.frame, subelement)
                widget.grid(column = grid_info[0],
                            row = grid_info[1],
                            columnspan = grid_info[2],
                            sticky = Tk.constants.W +
                                     Tk.constants.E + 
                                     Tk.constants.N + 
                                     Tk.constants.S,
                            padx = 2,
                            pady = 2)

        else:
            options = element.attrib
            if('row' in options.keys()):
                row = options['row']
                options.pop('row')
            if('column' in options.keys()):
                col = options['column']
                options.pop('column')
            if('rowspan' in options.keys()):
                rowspan = options['rowspan']
                options.pop('rowspan')
            else:
                rowspan = 1
            if('columnspan' in options.keys()):
                colspan = options['columnspan']
                options.pop('columnspan')
            else:
                colspan = 1
            widget_factory = getattr(Tk, element.tag)
            widget = widget_factory(master, **options)

            for subelement in element:
                subwidget, grid_info = self._load_xml(widget, subelement)
                subwidget.grid(column = grid_info[0],
                                row = grid_info[1],
                                columnspan = grid_info[2],
                                sticky = Tk.constants.W +
                                         Tk.constants.E + 
                                         Tk.constants.N + 
                                         Tk.constants.S,
                                padx = 2,
                                pady = 2)

            if(element.tag == "Button"):
                cmd = getattr(self, options['name']+"_Click")
                widget.config(command = cmd)
            elif(element.tag == "Radiobutton"):
                cmd = getattr(self, options['name']+"_Click")
                widget.config(command = cmd)
            elif(element.tag == "Checkbutton"):
                c = Tk.IntVar()
                cmd = getattr(self, options['name']+"_Click")
                widget.config(variable = c, command = cmd)
                self.variables[options['name']] = c
            elif(element.tag == "Entry"):
                c = Tk.StringVar()
                widget.config(textvariable = c)
                self.variables[options['name']] = c
            elif(element.tag == "Label"):
                c = Tk.StringVar()
                widget.config(textvariable = c)
                self.variables[options['name']] = c
            elif(element.tag == "Canvas"):
                widget.config(cursor = "cross")
            elif(element.tag == "Canvas"):
                c = Tk.Inter()
                cmd = getattr(self, options['name']+"_Change")
                widget.config(variable = c, command = cmd)
            self.elements[options['name']] = widget

            return widget, [col, row, colspan]

    def _print_console(self, msg):
        self.console.set(msg)

    # Find element by name(internal, depreciated)
    # Depreciated because of its UNSTABLITY
    def _find_by_name(self, parent, name):
        items = parent.children
        if name in items.keys():
            return items[name]
        else:
            for key in items.keys():
                if hasattr(items[key], 'children') and len(items[key].children) > 0:
                    return self._find_by_name(items[key], name)
            raise KeyError('Tk widget with the name "' + name + '" not found')

    def find(self, name):
        # Depreciated because of its UNSTABLITY
        #return self._find_by_name(self.frame, name)
        return self.elements[name]

    def get_func_name(self, back=0):
        name = sys._getframe(back + 1).f_code.co_name
        return name

    def set(self, name, value):
        self.variables[name].set(value)

    def get(self, name):
        return self.variables[name].get()

    def set_bg_color(self, name, color):
        self.find(name).config(bg = color)

    def set_fg_color(self, name, color):
        self.find(name).config(fg = color)

    def set_text_bold(self, name):
        bolded = font.Font(family='D2Coding', weight='bold', size='10')
        self.find(name).config(font=bolded)

    def set_title(self, title):
        self.root.title(title + " " + self.root.title())

    def print(self, mode, string):
        if(mode not in ["INFO", "FUNC", "WARN", "ERR"]):
            return
        msg = mode + " : " + string
        print(msg)
        #print("\n" + msg + "\n")
        self._print_console(msg)

    def terminate(self):
        print('')
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print('@@@@@ Terminate Program @@@@@')
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
        print('')
        self.flag_terminate = True
