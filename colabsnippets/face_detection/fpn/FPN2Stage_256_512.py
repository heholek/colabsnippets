import tensorflow as tf

from colabsnippets.face_detection.fpn.FPN2StageBase import FPN2StageBase
from colabsnippets.ops import conv2d, reduction_block, main_block


class FPN2Stage_256_512(FPN2StageBase):
  def __init__(self, name='fpn2stage_256_512'):
    super().__init__(name=name, stage_filters=[256, 512], out_channels=256)

  def init_bottom_up_weights(self, weight_processor):
    weight_processor.process_conv_weights(3, 16, 'conv_in', filter_size=3)
    weight_processor.process_reduction_block_weights(16, 32, 'reduction_block_0')
    weight_processor.process_reduction_block_weights(32, 64, 'reduction_block_1')
    weight_processor.process_reduction_block_weights(64, 128, 'reduction_block_2')
    weight_processor.process_reduction_block_weights(128, 256, 'reduction_block_3')
    weight_processor.process_main_block_weights(256, 'main_block_3_0')
    weight_processor.process_reduction_block_weights(256, 512, 'reduction_block_4')
    weight_processor.process_main_block_weights(512, 'main_block_4_0')

  def bottom_up(self, x):
    out = tf.nn.relu(conv2d(x, 'conv_in', [1, 2, 2, 1]))
    out = reduction_block(out, 'reduction_block_0', is_activate_input=False)
    out = reduction_block(out, 'reduction_block_1')
    out = reduction_block(out, 'reduction_block_2')
    out = reduction_block(out, 'reduction_block_3')
    out1 = out = main_block(out, 'main_block_3_0')
    out = reduction_block(out, 'reduction_block_4')
    out2 = out = main_block(out, 'main_block_4_0')

    return out1, out2
