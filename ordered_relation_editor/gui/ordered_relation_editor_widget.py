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
from qgis.gui import QgsAbstractRelationEditorWidget


class OrderedRelationEditorWidget(QgsAbstractRelationEditorWidget):

    def __init__(self, config, parent):
        super().__init__(config, parent)


    def config(self):
        return {

        }

    def setConfig(self, config):
        pass
