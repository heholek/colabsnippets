import cv2

from colabsnippets.utils import fix_boxes, abs_bbox_coords, rel_bbox_coords


class AlbumentationsAugmentorBase:
  def __init__(self, albumentations_lib):
    self.albumentations_lib = albumentations_lib
    self.bbox_params = self.albumentations_lib.BboxParams(format='coco', label_fields=['labels'], min_area=0.0,
                                                          min_visibility=0.0)
    self.log_augmentation_exception = False

  def _fix_rel_boxes(self, boxes):
    fixed_boxes = []
    for x, y, w, h in boxes:
      x, y = max(0, x), max(0, y)
      w, h = min(1.0 - x, w), min(1.0 - y, h)
      if x >= 0.9999 or y >= 0.9999 or w <= 0.001 or h <= 0.001:
        continue
      fixed_boxes.append((x, y, w, h))
    return fixed_boxes

  def _fix_abs_boxes(self, abs_boxes, hw):
    return [abs_bbox_coords(rel_box, hw) for rel_box in self._fix_rel_boxes([rel_bbox_coords(abs_box, hw) for abs_box in abs_boxes])]

  def _augment_abs_boxes(self, img, boxes, resize):
    raise Exception("AlbumentationsAugmentorBase - _augment_abs_boxes not implemented")

  def augment(self, img, boxes=[], image_size=None):
    try:
      _boxes = fix_boxes([abs_bbox_coords(box, img.shape[0:2]) for box in self._fix_rel_boxes(boxes)], max(img.shape[0:2]),
                        1)
      _img, _boxes = self._augment_abs_boxes(img, _boxes, image_size)
      _boxes = [rel_bbox_coords(box, _img.shape[0:2]) for box in _boxes]
      return _img, _boxes
    except:
      if self.log_augmentation_exception:
        print("failed to augment")
      return img, boxes

  def resize_and_to_square(self, img, boxes=[], image_size=None):
    boxes = fix_boxes([abs_bbox_coords(box, img.shape[0:2]) for box in self._fix_rel_boxes(boxes)], max(img.shape[0:2]),
                      1)
    transforms = self.albumentations_lib.augmentations.transforms
    Compose = self.albumentations_lib.Compose
    res = Compose([
      transforms.LongestMaxSize(p=1.0, max_size=image_size),
      transforms.PadIfNeeded(p=1.0, min_height=image_size, min_width=image_size, border_mode=cv2.BORDER_CONSTANT)
    ], self.bbox_params)(image=img, bboxes=boxes, labels=['' for _ in boxes])
    img, boxes = res['image'], res['bboxes']
    boxes = [rel_bbox_coords(box, img.shape[0:2]) for box in boxes]
    return img, boxes
