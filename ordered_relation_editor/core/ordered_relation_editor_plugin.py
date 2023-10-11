# -----------------------------------------------------------
#
# QGIS Ordered Relation Editor Plugin
# Copyright (C) 2020 Denis Rouzaud
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

import os

from qgis.gui import QgisInterface, QgsGui
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QObject, QSettings, QTranslator

from ordered_relation_editor.gui.ordered_relation_editor_widget_factory import (
    WIDGET_TYPE,
    OrderedRelationEditorWidgetFactory,
)

DEBUG = True


class OrderedRelationEditorPlugin(QObject):
    plugin_name = "&Ordered Relation Editor"

    def __init__(self, iface: QgisInterface):
        QObject.__init__(self)
        self.iface = iface

        # initialize translation
        qgis_locale = QLocale(QSettings().value("locale/userLocale"))
        locale_path = os.path.join(os.path.dirname(__file__), "i18n")
        self.translator = QTranslator()
        self.translator.load(qgis_locale, "actions_for_relations", "_", locale_path)
        QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        QgsGui.relationWidgetRegistry().addRelationWidget(
            OrderedRelationEditorWidgetFactory()
        )

    def unload(self):
        QgsGui.relationWidgetRegistry().removeRelationWidget(WIDGET_TYPE)
