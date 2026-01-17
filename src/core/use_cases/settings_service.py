from src.core.domain.settings_provider import SettingsProvider
from .response import Response


class SettingsServices:
    def __init__(self, settings_provider: SettingsProvider):
        self._settings_provider = settings_provider

    def get_default_bible(self):
        bible = self._settings_provider.get_settings("bible")
        if bible:
            return Response(
                success=True, code="verse.bible_getted", data=bible
            ).to_dict()
        return Response(success=False, code="verse.bible_not_found").to_dict()

    def set_defautl_bible(self, bible: dict):
        self._settings_provider.set_settings("bible", bible)
        return Response(success=True, code="verse.bible_setted").to_dict()

    def get_default_media_folder(self):
        media_folder = self._settings_provider.get_settings("media_folder")
        if media_folder:
            return Response(
                success=True, code="media.folder_getted", data=media_folder
            ).to_dict()
        return Response(success=False, code="media.folder_not_found").to_dict()

    def set_defautl_media_folder(self, media_folder: str):
        self._settings_provider.set_settings("media_folder", media_folder)
        return Response(success=True, code="media.folder_setted").to_dict()

    def get_default_slide_style(self):
        slide_style = self._settings_provider.get_settings("slide_style")
        if slide_style:
            return Response(
                success=True, code="sv.slide_style_getted", data=slide_style
            ).to_dict()
        return Response(success=False, code="sv.slide_style_not_found").to_dict()

    def set_defautl_slide_style(self, slide_style: dict):
        self._settings_provider.set_settings("slide_style", slide_style)
        return Response(success=True, code="sv.slide_style_setted").to_dict()

    def get_default_theme(self):
        theme = self._settings_provider.get_settings("theme")
        if theme:
            return Response(success=True, code="sv.theme_getted", data=theme).to_dict()
        return Response(success=False, code="sv.theme_not_found").to_dict()

    def set_defautl_theme(self, theme: str):
        self._settings_provider.set_settings("theme", theme)
        return Response(success=True, code="sv.theme_setted").to_dict()
