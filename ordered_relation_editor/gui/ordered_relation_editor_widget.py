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
from qgis.core import QgsFeature, QgsApplication
from qgis.gui import QgsAbstractRelationEditorWidget, QgsAttributeForm, QgsScrollArea
from ordered_relation_editor.core.ordered_relation_model import OrderedRelationModel

WidgetUi, _ = loadUiType(os.path.join(os.path.dirname(__file__), '../ui/ordered_relation_editor_widget.ui'))


class OrderedRelationEditorWidget(QgsAbstractRelationEditorWidget, WidgetUi):

    def __init__(self, config, parent):
        super().__init__(config, parent)
        self.setupUi(self)
        self.addFeatureToolButton.setIcon(QgsApplication.getThemeIcon('/mActionNewTableRow.svg'))
        self.addFeatureToolButton.clicked.connect(self.addFeature)
        self.attribute_form = None

        print('__init__ OrderedRelationEditorWidget')

        self.ordering_field = str()
        self.image_path = str()
        self.description = str()

        self.model = OrderedRelationModel()
        self.model.currentFeatureChanged.connect(self.onCurrentFeatureChanged)

        # QML display of images
        layout = QVBoxLayout()
        self.mListView.setLayout(layout)
        self.view = QQuickWidget(self.mListView)
        self.view.rootContext().setContextProperty("orderedModel", self.model)
        self.view.setSource(QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), '../qml/OrderedImageList.qml')))
        layout.addWidget(self.view)

    def config(self):
        return {

        }

    def setConfig(self, config):
        self.ordering_field = config['ordering_field']
        self.image_path = config['image_path']
        self.description = config['description']

    def beforeSetRelationFeature(self, new_relation, new_feature):
        layer = self.relation().referencingLayer()
        if layer:
            layer.editingStarted.disconnect(self.update_buttons)
            layer.editingStopped.disconnect(self.update_buttons)
        if self.attribute_form:
            if self.relation().isValid() and self.relation().referencingLayer().isEditable():
                self.attribute_form.save()
        self.view.rootObject().clearIndex()

    def afterSetRelationFeature(self):
        layer = self.relation().referencingLayer()
        if layer:
            layer.editingStarted.connect(self.update_buttons)
            layer.editingStopped.connect(self.update_buttons)

    def update_buttons(self):
        enabled = self.relation().isValid() and self.relation().referencingLayer().isEditable()
        self.addFeatureToolButton.setEnabled(enabled)

    def updateUi(self):
        # print('updateUi')
        self.model.init(self.relation(), self.ordering_field, self.feature(), self.image_path, self.description)

        # form view
        if self.attribute_form:
            self.attribute_form.deleteLater()
        self.attribute_form = QgsAttributeForm(self.relation().referencingLayer(), QgsFeature(), self.editorContext())
        if not self.editorContext().parentContext():
            attribute_editor_scroll_area = QgsScrollArea()
            attribute_editor_scroll_area.setWidgetResizable(True)
            self.mAttributeFormView.layout().addWidget(attribute_editor_scroll_area)
            attribute_editor_scroll_area.setWidget(self.attribute_form)
        else:
            self.mAttributeFormView.layout().addWidget(self.attribute_form)

        self.update_buttons()
        self.view.rootObject().clearIndex()


    def parentFormValueChanged(self, attribute, newValue):
        if self.attribute_form:
            self.attribute_form.parentFormValueChanged(attribute, newValue)

    def onCurrentFeatureChanged(self, feature):
        if self.attribute_form:
            if self.relation().referencingLayer().isEditable():
                if self.attribute_form.save():
                    self.model.reloadData()

            self.attribute_form.setFeature(feature)


