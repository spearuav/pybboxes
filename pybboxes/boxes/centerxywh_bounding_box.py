from typing import Tuple, Union

from pybboxes.boxes.base import BaseBoundingBox
from pybboxes.boxes.bbox import BoundingBox


class CenterxywhBoundingBox(BaseBoundingBox):
    def __init__(
        self,
        x_c: int,
        y_c: int,
        w: int,
        h: int,
        image_size: Tuple[int, int],
        strict: bool = False,
    ):
        super(CenterxywhBoundingBox, self).__init__(x_c, y_c, w, h, image_size=image_size, strict=strict)

    def _validate_values(self, *values):
        x_c, y_c, w, h = values
        image_width, image_height = self.image_size
        if w <= 0 or h <= 0:
            raise ValueError("Given width and height must be greater than 0.")
        elif self.strict and (x_c < 0 or y_c < 0):
            raise ValueError("Given top-left point is out of bounds.")
        elif (image_width is not None and x_c + w/2 > image_width) or (
                image_width is not None and y_c + h/2 > image_height
        ):
            if self.strict:
                raise ValueError(
                    "Given bounding box values is out of bounds. "
                    "To silently skip out of bounds cases pass 'strict=False'."
                )
            self._is_oob = True
        elif not self.is_image_size_null():
            self._is_oob = False

    def to_voc(self, return_values: bool = False) -> Union[Tuple[int, int, int, int], "BoundingBox"]:
        x_c, y_c, w, h = self.values
        x_tl = x_c - w / 2
        y_tl = y_c - h / 2
        x_br = x_tl + w
        y_br = y_tl + h

        x_tl, y_tl, x_br, y_br = round(x_tl), round(y_tl), round(x_br), round(y_br)
        if return_values:
            return x_tl, y_tl, x_br, y_br
        return BoundingBox(x_tl, y_tl, x_br, y_br, image_size=self.image_size, strict=self.strict)

    @classmethod
    def from_voc(
        cls,
        x_tl: int,
        y_tl: int,
        x_br: int,
        y_br: int,
        image_size: Tuple[int, int] = None,
        strict: bool = False,
    ) -> "CenterxywhBoundingBox":
        if image_size is None:
            raise ValueError("CenterXyhbBoundingBox box requires `image_size` to scale the box values.")

        w = x_br - x_tl
        h = y_br - y_tl
        x_c = x_tl + int(round(w / 2))
        y_c = y_tl + int(round(h / 2))
        return cls(x_c, y_c, w, h, image_size=image_size, strict=strict)