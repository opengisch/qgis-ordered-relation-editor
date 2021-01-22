# -*- coding: utf-8 -*-
# -----------------------------------------------------------
#
# QGIS Ordered Relation Editor Plugin
# Copyright (C) 2020 Denis Rouzaud
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

from PyQt5.QtQuickWidgets import QQuickWidget
import os
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtWidgets import QVBoxLayout
from qgis.PyQt.uic import loadUiType
from qgis.gui import QgsAbstractRelationEditorWidget

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../ui/ordered_relation_editor_widget.ui'))


class OrderedRelationEditorWidget(QgsAbstractRelationEditorWidget, WidgetUi):

    def __init__(self, config, parent):
        super().__init__(config, parent)
        self.setupUi(self)

        layout = QVBoxLayout()
        view = QQuickWidget()
        view.setSource(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../qml/OrderedImageList.qml')))
        layout.addWidget(view)
        self.mListView.setLayout(layout)

    def config(self):
        return {

        }

    def setConfig(self, config):
        pass
