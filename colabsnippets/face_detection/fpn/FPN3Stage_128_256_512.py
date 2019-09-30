import tensorflow as tf

from .FPN3StageBase import FPN3StageBase
from ...ops import conv2d, reduction_block, main_block


class FPN3Stage_128_256_512(FPN3StageBase):
  def __init__(self, name='fpn3stage_128_256_512', with_batch_norm=True):
    self.with_batch_norm = with_batch_norm
    super().__init__(name=name, stage_filters=[128, 256, 512],
                     with_detection_module=True, use_minimal_anchors=True, net_suffix="", out_channels=128,
                     with_batch_norm=True)

  def init_bottom_up_weights(self, weight_processor):
    weight_processor.process_conv_weights(3, 8, 'conv_in', filter_size=3, with_batch_norm=self.with_batch_norm)
    weight_processor.process_reduction_block_weights(8, 16, 'reduction_block_0', with_batch_norm=self.with_batch_norm)
    weight_processor.process_depthwise_separable_conv2d_weights(16, 32, 'separable_conv0',
                                                                with_batch_norm=self.with_batch_norm)
    weight_processor.process_reduction_block_weights(32, 64, 'reduction_block_1', with_batch_norm=self.with_batch_norm)
    weight_processor.process_depthwise_separable_conv2d_weights(64, 128, 'separable_conv1',
                                                                with_batch_norm=self.with_batch_norm)
    weight_processor.process_main_block_weights(128, 'main_block_1_0', with_batch_norm=self.with_batch_norm)
    weight_processor.process_reduction_block_weights(128, 256, 'reduction_block_2',
                                                     with_batch_norm=self.with_batch_norm)
    weight_processor.process_main_block_weights(256, 'main_block_2_0', with_batch_norm=self.with_batch_norm)
    weight_processor.process_reduction_block_weights(256, 512, 'reduction_block_3',
                                                     with_batch_norm=self.with_batch_norm)
    weight_processor.process_main_block_weights(512, 'main_block_3_0', with_batch_norm=self.with_batch_norm)

  def bottom_up(self, x):
    out = tf.nn.relu(conv2d(x, 'conv_in', [1, 2, 2, 1], with_batch_norm=self.with_batch_norm))
    out = reduction_block(out, 'reduction_block_0', is_activate_input=False, with_batch_norm=self.with_batch_norm)
    out = reduction_block(out, 'reduction_block_1', with_batch_norm=self.with_batch_norm)
    out1 = out = main_block(out, 'main_block_1_0', with_batch_norm=self.with_batch_norm)
    out = reduction_block(out, 'reduction_block_2', with_batch_norm=self.with_batch_norm)
    out2 = out = main_block(out, 'main_block_2_0', with_batch_norm=self.with_batch_norm)
    out = reduction_block(out, 'reduction_block_3', with_batch_norm=self.with_batch_norm)
    out3 = main_block(out, 'main_block_3_0', with_batch_norm=self.with_batch_norm)

    return out1, out2, out3
