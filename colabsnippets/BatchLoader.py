import cv2
import numpy as np

from .utils import shuffle_array
from .preprocess import resize_preserve_aspect_ratio, pad_to_square

class BatchLoader:
  def __init__(
    self,
    data,
    resolve_image_path,
    extract_data_labels,
    augment_image = None,
    is_test = False,
    start_epoch = None
  ):
    if not is_test and start_epoch == None:
      raise Exception('DataLoader - start_epoch has to be defined in train mode')

    self.data = data
    self.resolve_image_path = resolve_image_path
    self.extract_data_labels = extract_data_labels
    self.augment_image = augment_image
    self.is_test = is_test
    self.epoch = start_epoch
    self.buffered_data = shuffle_array(self.data) if not is_test else self.data
    self.current_idx = 0

  def get_end_idx(self):
    return len(self.buffered_data)

  def load_image(self, data, image_size):
    db = data['db']
    img_file = data['file']
    file_suffix = 'chip_0' if db == 'utk' else ('face_0' if db == 'appareal' else '')
    landmarks_file = img_file.replace(file_suffix + '.jpg', file_suffix + '.json')
    landmarks_file_path = './data/' + db + '/landmarks/' + landmarks_file

    img = cv2.imread(self.resolve_image_path(data))
    if img is None:
      raise Exception('failed to read image from path: ' + img_file_path)

    if (self.augment_image is not None):
      img = self.augment_image(img, data)

    img = pad_to_square(resize_preserve_aspect_ratio(img, image_size))

    return img

  def load_image_batch(self, datas, image_size):
    preprocessed_imgs = []
    for data in datas:
      preprocessed_imgs.append(self.load_image(data, image_size))
    return np.stack(preprocessed_imgs, axis = 0)

  def load_labels(self, datas):
    labels = []
    for data in datas:
      labels.append(self.extract_data_labels(data))
    return np.stack(labels, axis = 0)

  def next_batch(self, batch_size, image_size = 112):
    if batch_size < 1:
      raise Exception('DataLoader.next_batch - invalid batch_size: ' + str(batch_size))


    from_idx = self.current_idx
    to_idx = self.current_idx + batch_size

    # end of epoch
    if (to_idx > len(self.buffered_data)):
      if self.is_test:
        to_idx = len(self.buffered_data)
        if to_idx == self.current_idx:
          return None
      else:
        self.epoch += 1
        self.buffered_data = self.buffered_data[from_idx:] + shuffle_array(self.data)
        from_idx = 0
        to_idx = batch_size

    self.current_idx = to_idx

    next_data = self.buffered_data[from_idx:to_idx]

    batch_x = self.load_image_batch(next_data, image_size)
    batch_y = self.load_labels(next_data)

    return batch_x, batch_y