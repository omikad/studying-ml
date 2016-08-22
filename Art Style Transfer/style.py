'''

Simple script implementing artistic style transfer based on the work of Gatys et al. (http://arxiv.org/abs/1508.06576)
VGG implementation for Tensorflow taken from https://github.com/machrisaa/tensorflow-vgg and slightly modified.

by Jan Ivanecky
MIT license

'''

import argparse
import numpy as np
import tensorflow as tf
import vgg
from PIL import Image

def load_image(path, args_crop, shape=None, scale=1.0):
    img = Image.open(path)
    
    if shape is not None:
        # crop to obtain identical aspect ratio to shape
        width, height = img.size
        target_width, target_height = shape[0], shape[1]

        aspect_ratio = width / float(height)
        target_aspect = target_width / float(target_height)
        
        if aspect_ratio > target_aspect: # if wider than wanted, crop the width
            new_width = int(height * target_aspect)
            if args_crop == 'right':
                img = img.crop((width - new_width, 0, width, height))
            elif args_crop == 'left':
                img = img.crop((0, 0, new_width, height))
            else:
                img = img.crop(((width - new_width) / 2, 0, (width + new_width) / 2, height))
        else: # else crop the height
            new_height = int(width / target_aspect)
            if args_crop == 'top':
                img = img.crop((0, 0, width, new_height))
            elif args_crop == 'bottom':
                img = img.crop((0, height - new_height, width, height))
            else:
                img = img.crop((0, (height - new_height) / 2, width, (height + new_height) / 2))

        # resize to target now that we have the correct aspect ratio
        img = img.resize((target_width, target_height))
    
    # rescale
    w,h = img.size
    img = img.resize((int(w * scale), int(h * scale)))
    img.show()
    img = np.array(img)
    img = img / 255.0
    return img

def gram_matrix(activations):
    height = tf.shape(activations)[1]
    width = tf.shape(activations)[2]
    num_channels = tf.shape(activations)[3]
    gram_matrix = tf.transpose(activations, [0, 3, 1, 2]) 
    gram_matrix = tf.reshape(gram_matrix, [num_channels, width * height])
    gram_matrix = tf.matmul(gram_matrix, gram_matrix, transpose_b=True)
    return gram_matrix

def content_loss(const_layer, var_layer):
    diff = const_layer - var_layer
    diff_squared = diff * diff
    sum = tf.reduce_sum(diff_squared) / 2.0
    return sum

def style_loss(const_layers, var_layers):
    loss_style = 0.0
    layer_count = float(len(const_layers))
    for const_layer, var_layer in zip(const_layers, var_layers):        
        gram_matrix_const = gram_matrix(const_layer)
        gram_matrix_var = gram_matrix(var_layer)
        
        size = tf.to_float(tf.size(const_layer))
        diff_style = gram_matrix_const - gram_matrix_var
        diff_style_sum = tf.reduce_sum(diff_style * diff_style) / (4.0 * size * size)
        loss_style += diff_style_sum
    return loss_style / layer_count
