from engine.entity.base import Base


def update_boxes(self: Base, value: dict = {}, **kwarg) -> None:
    """List of boxes for each of the box types. Not needed outside of box types."""
    for box_type in value:
        try:
            if box_type in self.boxes:
                self.boxes[box_type] = dict(
                    self.boxes.get(box_type, {}) | value[box_type]
                )
                if value[box_type].get("hitreg", None) != None:
                    self.hitreg[box_type].clear()
        except:
            pass


def set_boxes(self: Base, value: dict = {}, **kwarg) -> None:
    """List of boxes for each of the box types. Not needed outside of box types."""
    for box_type in value:
        try:
            if box_type in self.boxes:
                self.boxes[box_type] = dict(value[box_type])
                self.hitreg[box_type].clear()
        except:
            pass


BOXES_ACT = {
    "boxes": update_boxes,
    "set_boxes": set_boxes,
}
