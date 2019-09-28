import json
import random
import os
import tensorflow as tf
import numpy as np

from .drive import get_global_drive_instance

def load_json(json_file_path):
  with open(json_file_path) as json_file:
    return json.load(json_file)

def shuffle_array(arr):
  arr_clone = arr[:]
  random.shuffle(arr_clone)
  return arr_clone

def load_json_if_exists(filepath):
  return load_json(filepath) if os.path.exists(filepath) else []

def save_meta_json(var_list, filename):
  meta_data = []
  for var in var_list:
    meta_data.append({ 'shape': var.get_shape().as_list(), 'name': var.name })
  meta_json = open(filename + '.json', 'w')
  meta_json.write(json.dumps(meta_data))
  meta_json.close()

def save_weights(var_list, filename):
  checkpoint_data = np.array([], dtype = 'float32')
  for var in var_list:
    checkpoint_data = np.append(checkpoint_data, var.eval().flatten())
  np.save(filename, checkpoint_data)

# auto recompile ops in case of new batch size
def forward_factory(compile_forward_op, batch_size, image_size):
  X = tf.placeholder(tf.float32, [batch_size, image_size, image_size, 3])
  forward_op = compile_forward_op(X)

  def forward(sess, batch_x):
    local_X, local_forward_op = X, forward_op
    if batch_x.shape[0] != X.shape[0]:
      local_X = tf.placeholder(tf.float32, [batch_x.shape[0], image_size, image_size, 3])
      local_forward_op = compile_forward_op(local_X)
    return sess.run(local_forward_op, feed_dict = { local_X: batch_x })

  return forward

def mk_dir_if_not_exists(dir_path):
  if not os.path.exists(dir_path):
    os.makedirs(dir_path)

def flatten_list(l):
  return [item for sublist in l for item in sublist]

def try_upload_file(filename, drive_upload_folder_id):
  try:
    upload = get_global_drive_instance().CreateFile({ "title": filename, "parents": [{"kind": "drive#fileLink", "id": drive_upload_folder_id }] })
    upload.SetContentFile(filename)
    upload.Upload()
  except Exception as e:
    print ("failed to upload " + filename)
    print (e)

def gpu_session(callback, device_name = '/gpu:0'):
  config = tf.ConfigProto()
  config.gpu_options.allow_growth = True
  config.allow_soft_placement = True
  config.log_device_placement = True
  with tf.Session(config = config) as session:
    with tf.device(device_name):
      return callback(session)

def fix_boxes(boxes, image_size, min_box_size_px):
  out_boxes = []
  for box in boxes:
    x, y, w, h = box

    if (image_size*w) <= min_box_size_px or (image_size*h) <= min_box_size_px:
      continue

    out_boxes.append(box)

  return out_boxes