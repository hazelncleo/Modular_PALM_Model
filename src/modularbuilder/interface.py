from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Center
from textual.widgets import Button, Header, Footer, Static, Tabs, Tab, ListView, ListItem, Label


class ModularBuilderApp(App):

    CSS_PATH='interface.tcss'

    def compose(self) -> ComposeResult:
        self.header = Header()
        self.commandlist = ListView(
            ListItem(Label('Object Commands')),
            ListItem(Label('Model Commands')),
            ListItem(Label('Database Commands')),
            ListItem(Label('Settings')),
            ListItem(Label('Quit'))
        )
        self.tabbedinfo = Tabs(
            Tab('Database Tree'),
            Tab('Database Info'),
            Tab('File Structure'),
            Tab('Log')
        )
        self.tabbedcontainer = Center(self.tabbedinfo)
        self.footer = Footer()


        yield self.header
        yield Horizontal(
            self.commandlist,
            self.tabbedcontainer
        )
        yield self.footer

    def on_mount(self) -> None:

        self.commandlist.border_title = 'Commands'
        self.tabbedcontainer.border_title = 'Info Tabs'

    






if __name__ == "__main__":
    app = ModularBuilderApp()
    app.run()