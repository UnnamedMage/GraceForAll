from ..Qtive.Managers import BaseApp
from .pages.main import MainView, MainViewModel
from .modals.song_editor import SongEditor, SongEditorVM
from .modals.save_manager import SaveManager, SaveManagerVM
from .modals.open_manager import OpenManager, OpenManagerVM
from .modals.about import About, AboutVM
from .modals.settings_manager import SettingsManager, SettingsManagerVM
from ..core.factory import Factory


class App(BaseApp):
    def _pre_init(self):
        self.factory = Factory()
        self.import_version()

    def import_version(self):
        import_service = self.factory.get_import_service()
        import_service.verify_ss()
        import_service.verify_conf()

    def _build_app(self):
        self.mainvm = MainViewModel(self.factory)
        self.mainview = MainView()
        self.mainvm.pv_init()
        self.mainview.setWindowTitle("GraceForAll")
        self.mainvm.window.close.connect(self.mainview.close)
        self.mainvm.window.minimize.connect(self.mainview.showMinimized)
        self.mainvm.window.restore.connect(self.mainview.toggle_size)
        self.mainvm.window.move.connect(self.mainview.move_window)
        self.mainvm.app.song_editor.connect(self.launch_song_editor)

        self.sevm = SongEditorVM(self.factory)
        self.seview = SongEditor()
        self.sevm.window.close.connect(self.seview.close)
        self.seview.setParent(self.mainview)
        self.seview.setWindowTitle("Editor de canciones")
        self.sevm.app.task_with_song.connect(self.mainvm.change_in_a_song)
        self.sevm.app.task_with_bg.connect(self.mainvm.ssc.refresh_menu)

        self.smvm = SaveManagerVM(self.factory)
        self.smview = SaveManager()
        self.smview.setParent(self.mainview)
        self.smvm.window.close.connect(self.smview.close)
        self.smvm.window.show.connect(self.smview.exec_)
        self.smvm.window.title.connect(self.smview.setWindowTitle)
        self.smvm.app.saved_schedule.connect(self.mainvm.sc.set_schedule)
        self.mainvm.app.save_manager.connect(self.smvm.request_receiver)

        self.omvm = OpenManagerVM(self.factory)
        self.omview = OpenManager()
        self.omview.setParent(self.mainview)
        self.omview.setWindowTitle("Abrir programa")
        self.omvm.window.close.connect(self.omview.close)
        self.omvm.app.send_to_show.connect(self.mainvm.sc.set_schedule)
        self.mainvm.app.open_manager.connect(self.launch_open_manager)
        self.omvm.app.send_to_eliminate.connect(self.mainvm.sc.change_in_schedule)
        self.smvm.app.schedule_added.connect(self.omvm.refresh_list)

        self.settingsvm = SettingsManagerVM(self.factory)
        self.settingsview = SettingsManager()
        self.settingsvm.pv_init()
        self.settingsview.setParent(self.mainview)
        self.settingsview.setWindowTitle("Configuracion")
        self.settingsvm.window.close.connect(self.settingsview.close)
        self.mainvm.app.settings_manager.connect(self.launch_settings_manager)

        self.avm = AboutVM()
        self.aview = About()
        self.aview.setParent(self.mainview)
        self.aview.setWindowTitle("Acerca de...")
        self.avm.window.close.connect(self.aview.close)
        self.mainvm.app.about.connect(self.aview.exec_)

    def _start_app(self):
        self.launch_main()

    def launch_main(self):
        self.mainview.show()
        self.mainvm.on_start()

    def launch_song_editor(self, song_id: str = None):
        if song_id:
            self.sevm.set_song_id(song_id)
        self.sevm.on_start()
        self.seview.exec_()

    def launch_open_manager(self):
        self.omvm.on_start()
        self.omview.exec_()

    def launch_settings_manager(self):
        self.settingsvm.on_start()
        self.settingsview.exec_()
