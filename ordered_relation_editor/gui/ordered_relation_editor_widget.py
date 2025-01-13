# -----------------------------------------------------------
#
# QGIS Ordered Relation Editor Plugin
# Copyright (C) 2020 Denis Rouzaud
#
# licensed under the terms of GNU GPL 2+
#
# -----------------------------------------------------------

import os

from qgis.core import QgsApplication, QgsFeature, QgsMessageLog
from qgis.gui import QgsAbstractRelationEditorWidget, QgsAttributeForm, QgsScrollArea
from qgis.PyQt.QtCore import QModelIndex, QTimer, QUrl

try:
    from qgis.PyQt.QtQuickWidgets import QQuickWidget
except ImportError:
    # https://github.com/qgis/QGIS/pull/60123
    from PyQt5.QtQuickWidgets import QQuickWidget
from qgis.PyQt.QtWidgets import QVBoxLayout
from qgis.PyQt.uic import loadUiType

from ordered_relation_editor.core.ordered_relation_model import OrderedRelationModel

WidgetUi, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), "../ui/ordered_relation_editor_widget.ui")
)

Debug = True


class OrderedRelationEditorWidget(QgsAbstractRelationEditorWidget, WidgetUi):
    def __init__(self, config, parent):
        super().__init__(config, parent)
        self.updateUiTimer = QTimer()
        self.updateUiTimer.setSingleShot(True)
        self.updateUiTimer.timeout.connect(self.updateUiTimeout)
        self.setupUi(self)
        self.addFeatureToolButton.setIcon(
            QgsApplication.getThemeIcon("/mActionNewTableRow.svg")
        )
        self.addFeatureToolButton.clicked.connect(self.addFeature)
        self.deleteFeatureToolButton.setIcon(
            QgsApplication.getThemeIcon("/mActionDeleteSelected.svg")
        )
        self.deleteFeatureToolButton.clicked.connect(self.deleteSelectedFeature)
        self.attribute_form = None

        print("__init__ OrderedRelationEditorWidget")

        self.ordering_field = ""
        self.image_path = ""
        self.description = ""

        self.model = OrderedRelationModel()
        self.model.currentFeatureChanged.connect(self.onCurrentFeatureChanged)

        # QML display of images
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.mListView.setLayout(layout)
        self.mListView.setMinimumHeight(200)
        self.mListView.setMaximumWidth(300)
        self.view = QQuickWidget(self.mListView)
        self.view.rootContext().setContextProperty("orderedModel", self.model)
        self.view.setSource(
            QUrl.fromLocalFile(
                os.path.join(os.path.dirname(__file__), "../qml/OrderedImageList.qml")
            )
        )
        self.view.setResizeMode(QQuickWidget.SizeRootObjectToView)
        layout.addWidget(self.view)

    def config(self):
        return {}

    def setConfig(self, config):
        self.ordering_field = config["ordering_field"]
        self.image_path = config["image_path"]
        self.description = config["description"]

    def beforeSetRelationFeature(self, new_relation, new_feature):
        layer = self.relation().referencingLayer()
        if layer:
            layer.editingStarted.disconnect(self.update_buttons)
            layer.editingStopped.disconnect(self.update_buttons)
        if self.attribute_form:
            if (
                self.relation().isValid()
                and self.relation().referencingLayer().isEditable()
            ):
                self.attribute_form.save()
        self.view.rootObject().clearIndex()

    def afterSetRelationFeature(self):
        layer = self.relation().referencingLayer()
        if layer:
            layer.editingStarted.connect(self.update_buttons)
            layer.editingStopped.connect(self.update_buttons)

    def update_buttons(self):
        enabled = (
            self.relation().isValid()
            and self.relation().referencingLayer().isEditable()
        )
        view_has_selection = self.view.rootObject().currentIndex() >= 0
        self.addFeatureToolButton.setEnabled(enabled)
        self.deleteFeatureToolButton.setEnabled(enabled and view_has_selection)

    def updateUi(self):
        self.updateUiTimer.start(200)

    def updateUiTimeout(self):
        if Debug:
            QgsMessageLog.logMessage("updateUiTimeout()")

        self.model.init(
            self.relation(),
            self.ordering_field,
            self.feature(),
            self.image_path,
            self.description,
        )

        # we defer attribute form creation on the first valid feature passed on
        if self.attribute_form:
            self.attribute_form.deleteLater()

        self.update_buttons()
        self.view.rootObject().setCurrentIndex(-1)

    def parentFormValueChanged(self, attribute, newValue):
        if self.attribute_form:
            self.attribute_form.parentFormValueChanged(attribute, newValue)

    def onCurrentFeatureChanged(self, feature=QgsFeature()):
        if not self.attribute_form and feature.isValid():
            self.attribute_form = QgsAttributeForm(
                self.relation().referencingLayer(), feature, self.editorContext()
            )
            if not self.editorContext().parentContext():
                attribute_editor_scroll_area = QgsScrollArea()
                attribute_editor_scroll_area.setWidgetResizable(True)
                self.mAttributeFormView.layout().addWidget(attribute_editor_scroll_area)
                attribute_editor_scroll_area.setWidget(self.attribute_form)
            else:
                self.mAttributeFormView.layout().addWidget(self.attribute_form)
        elif self.attribute_form:
            if self.relation().referencingLayer().isEditable():
                if self.attribute_form.save():
                    self.model.reloadData()

            if feature.isValid():
                self.attribute_form.setFeature(feature)
            else:
                self.attribute_form.deleteLater()
                self.attribute_form = None

        self.update_buttons()

    def deleteSelectedFeature(self):
        index = self.view.rootObject().currentIndex()
        if Debug:
            print("index", index)
        if index >= 0:
            feature_id = self.model.data(
                self.model.index(index, 0), OrderedRelationModel.FeatureIdRole
            )
            if Debug:
                print("fid", feature_id)
            self.deleteFeatures([feature_id])
