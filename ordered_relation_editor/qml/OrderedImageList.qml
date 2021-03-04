import QtQuick 2.14
import QtQuick.Controls 2.5
import QtQml.Models 2.14

Rectangle {
    id: root

    width: 300; height: 400

    Component {
        id: dragDelegate

        MouseArea {
            id: dragArea
            pressAndHoldInterval: 100
            enabled: orderedModel.layerEditingEnabled

            property bool held: false

            property int indexFrom: -1
            property int indexTo: -1

            anchors { left: parent.left; right: parent.right }
            height: content.height

            drag.target: held ? content : undefined
            drag.axis: Drag.YAxis

            onPressAndHold: held = true
            onReleased: {
               held = false
               orderedModel.moveitems(indexFrom, indexTo)
            }

            Rectangle {
                id: content
                anchors {
                    horizontalCenter: parent.horizontalCenter
                    verticalCenter: parent.verticalCenter
                }
                width: dragArea.width; height: row.implicitHeight + 4

                border.width: 1
                border.color: "lightsteelblue"

                color: dragArea.held ? "lightsteelblue" : "white"
                Behavior on color { ColorAnimation { duration: 100 } }

                radius: 2
                Drag.active: dragArea.held
                Drag.source: dragArea
                Drag.hotSpot.x: width / 2
                Drag.hotSpot.y: height / 2

                states: State {
                    when: dragArea.held

                    ParentChange { target: content; parent: root }
                    AnchorChanges {
                        target: content
                        anchors { horizontalCenter: undefined; verticalCenter: undefined }
                    }
                }

                Row {
                    id: row
                    anchors { fill: parent; margins: 2 }
                    Image { source: ImagePath }
                    Text { text: ImagePath }
                }
            }
            DropArea {
                anchors { fill: parent; margins: 10 }

                onEntered: {
                    if (dragArea.indexFrom === -1) dragArea.indexFrom = drag.source.DelegateModel.itemsIndex
                    dragArea.indexTo = dragArea.DelegateModel.itemsIndex
                    visualModel.items.move(
                            drag.source.DelegateModel.itemsIndex,
                            dragArea.DelegateModel.itemsIndex)
                }
            }
        }
    }
    DelegateModel {
        id: visualModel

        model: orderedModel
        delegate: dragDelegate
    }

    ListView {
        id: view

        anchors { fill: parent; margins: 2 }

        model: visualModel

        spacing: 4
        cacheBuffer: 50
    }
}
