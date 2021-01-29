# -*- coding: utf-8 -*-
"""1607729040_373__CI_HW3%2B%25285%2529.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jE1vksL1oTvjcFBohbb_ObAtK9vZNsSX
"""

!wget http://vision.stanford.edu/aditya86/ImageNetDogs/images.tar
# !wget http://files.heuritech.com/weights/alexnet_weights.h5
!tar -xf images.tar

# Commented out IPython magic to ensure Python compatibility.
# dataset ##################################
import os
from tensorflow import keras
import tensorflow as tf
assert tf.__version__.startswith('2')
from tensorflow.keras.layers.experimental.preprocessing import Rescaling
from tensorflow.keras.layers import *
tf.random.set_seed(1234)
!pip3 install tensorflow-datasets==1.2.0
import tensorflow_datasets as tfds
from matplotlib import pyplot as plt
import cv2 as cv
import numpy as np
import shutil
from pathlib import Path
import os
from keras.utils.data_utils import get_file
 
# %matplotlib inline
# %load_ext tensorboard


breeds = os.listdir("Images")

def get_breed_name(category):
  breed = breeds[np.where(category == 1)[0][0]]
  return breed.rsplit('-')[1]

def get_label_name(label):
  return get_breed_name(label.numpy())

def show_image(image):
  plt.imshow(image.numpy().astype("uint8"))
  plt.show()

# images_path = 'Images/'
images_path = Path("Images")
batch_size = 32

split_train, split_valid, split_test = 'train[:70%]', 'train[70%:]', 'test'


for folder in images_path.glob("*"):
  breed = str(folder).split("/")[1]
  os.rename(folder,os.path.join(images_path,breed))

np.random.seed(28)

if os.path.exists("./dataset"):
    shutil.rmtree("./dataset")
train_path = Path("./dataset/train")
test_path = Path("./dataset/test")

os.makedirs(train_path,exist_ok=True)
os.makedirs(test_path,exist_ok=True)

test_split=0.05
total_test_size=0
total_train_size=0

for breed_folder in images_path.glob("*"):

    breed = str(breed_folder).split("/")[-1]
    imgs = np.array(list(breed_folder.glob("*.jpg")))
    indices = np.random.permutation(len(imgs))

    test_size=int(len(imgs)*test_split)
    
    test_ds=imgs[indices[:test_size]]
    train_ds=imgs[indices[test_size:]]

    total_test_size += len(test_ds)
    total_train_size += len(train_ds)

    os.makedirs(os.path.join(train_path,breed),exist_ok=True)
    os.makedirs(os.path.join(test_path,breed),exist_ok=True)

    for im in test_ds:
        filename = f"{im.stem}.jpg"
        shutil.copy(im,os.path.join(test_path,breed,filename))

    for im in train_ds:
        filename = f"{im.stem}.jpg"
        shutil.copy(im,os.path.join(train_path,breed,filename)) 


print(f"train size: {total_train_size}")
print(f"test size: {total_test_size}")


def load_images():
  train_ds = keras.preprocessing.image_dataset_from_directory(train_path,
                                                                validation_split=0.2,
                                                                subset="training",
                                                                seed=28,
                                                                shuffle=True,
                                                                image_size=(227, 227),
                                                                batch_size=batch_size,
                                                                label_mode='categorical')
  valid_ds = keras.preprocessing.image_dataset_from_directory(train_path,
                                                                validation_split=0.2,
                                                                subset="validation",
                                                                seed=28,
                                                                image_size=(227, 227),
                                                                batch_size=batch_size,
                                                                label_mode='categorical')
  test_ds = keras.preprocessing.image_dataset_from_directory(test_path,
                                                                seed=28,
                                                                batch_size=batch_size,
                                                                image_size=(227, 227),
                                                                label_mode='categorical')
  train_ds = train_ds.prefetch(buffer_size=32)
  valid_ds = valid_ds.prefetch(buffer_size=32)
  return train_ds, valid_ds, test_ds

train_ds, val_ds, test_ds = load_images()

# preprocessing ##################
from sklearn.model_selection import train_test_split

def normalization(images):
  return (images / 255) - 0.5

# CNN ##################################
from keras.layers.normalization import BatchNormalization
from keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from keras.models import Sequential
import keras.layers as layers
from keras.utils.vis_utils import plot_model

data_augmentation = keras.Sequential(
  [
    layers.experimental.preprocessing.RandomRotation(0.2),
    layers.experimental.preprocessing.RandomZoom((0.1, 0.2), (0.1, 0.2)),
  ]
)

def alexNet(weights=None):
    model = Sequential()
    
    model.add(layers.Input(shape=(227, 227, 3)))
    model.add(data_augmentation)

    # 1 --> CONV
    model.add(Conv2D(filters=96, kernel_initializer='random_normal', kernel_size=(11, 11), strides=(4, 4), padding="valid", activation="relu"))
    # 1 --> POOLING (max pooling)
    model.add(MaxPooling2D(pool_size=(3, 3), strides=(2, 2)))
    model.add(BatchNormalization())

    # 2 --> CONV
    model.add(Conv2D(filters=256, kernel_size=(5, 5), strides=(1, 1), padding="valid", activation="relu"))
    # 2 --> POOLING (max pooling)
    model.add(MaxPooling2D(pool_size=(3, 3), strides=(2, 2)))
    model.add(BatchNormalization())

    # 3 --> CONV
    model.add(Conv2D(filters=384, kernel_size=(3, 3), strides=(1, 1), padding="valid", activation="relu"))

    # 4 --> CONV
    model.add(Conv2D(filters=384, kernel_size=(3, 3), strides=(1, 1), padding="valid", activation="relu"))

    # 5 --> CONV
    model.add(Conv2D(filters=256, kernel_size=(3, 3), strides=(1, 1), padding="valid", activation="relu"))
    # 5 --> POOLING (max pooling)
    model.add(MaxPooling2D(pool_size=(3, 3), strides=(2, 2)))
    model.add(BatchNormalization())

    model.add(Flatten())

    if weights is not None:
		   model.load_weights(weights)

    # 6 --> FULLY CONNECTED
    model.add(Dense(4096, input_shape=(227, 227, 3), activation="relu"))
    model.add(Dropout(0.5))
    model.add(BatchNormalization())

    # 7 --> FULLY CONNECTED
    model.add(Dense(4096, activation="relu"))
    model.add(Dropout(0.5))
    model.add(BatchNormalization())

    # 7 --> FULLY CONNECTED
    model.add(Dense(1000, activation="relu"))
    model.add(Dropout(0.5))
    model.add(BatchNormalization())

    # 8--> FULLY CONNECTED
    model.add(Dense(1000, activation="relu"))
    model.add(Dropout(0.5))
    model.add(BatchNormalization())

    model.add(Dense(len(breeds), activation="softmax"))

    model.compile(optimizer='adam', loss=keras.losses.CategoricalCrossentropy(from_logits=False), metrics=["accuracy"])
    model.summary()
    plot_model(model, to_file='model.png', show_shapes=True, show_layer_names=True)
    # plt.imshow("model.png")
    return model

model = alexNet()

from tensorflow.keras import layers
AUTOTUNE = tf.data.experimental.AUTOTUNE

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
normalization_layer = layers.experimental.preprocessing.Rescaling(1./255)
normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
epochs=40
history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs
)

# save model
model.save("my_h5_model.h5")
model.save_weights("weight_model.h5")

results = model.evaluate(test_ds)

# Xception with ready weights! ########

# load dataset again! #######

AUTOTUNE = tf.data.experimental.AUTOTUNE
train_path = Path("./dataset/train")
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    train_path,
    validation_split=0.2,
    seed=123,
    shuffle=True,
    image_size=(227, 227),
    batch_size=32,
    label_mode='categorical',
    subset='training')

val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    train_path,
    image_size=(227, 227),
    batch_size=32,
    seed=123,
    shuffle=True,
    validation_split=0.2,
    label_mode='categorical',
    subset='validation')
 
test_path = Path("./dataset/test")
test_ds = keras.preprocessing.image_dataset_from_directory(test_path,
                                                                seed=28,
                                                                batch_size=batch_size,
                                                                image_size=(227, 227),
                                                                label_mode='categorical')

def preprocess(data, label):
    data_preprocessed = keras.applications.xception.preprocess_input(data)
    return data_preprocessed, label


train_ds = train_ds.map(preprocess)
val_ds = val_ds.map(preprocess)
train_ds = train_ds.cache().shuffle(21000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

from keras.models import Model
from keras import layers
from keras.layers import Dense, Input, BatchNormalization, Activation
from keras.layers import Conv2D, SeparableConv2D, MaxPooling2D, GlobalAveragePooling2D, GlobalMaxPooling2D
from keras.utils.data_utils import get_file

def create_base_model():
  url = 'https://github.com/fchollet/deep-learning-models/releases/download/v0.4/xception_weights_tf_dim_ordering_tf_kernels_notop.h5'
  img_input =  keras.Input((227, 227, 3))

  # Block 1
  x = Conv2D(32,(3,3),strides=(2,2),use_bias=False)(img_input)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)
  x = Conv2D(64, (3, 3), use_bias=False)(x)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)
  residual = Conv2D(128, (1, 1), strides=(2, 2), padding='same', use_bias=False)(x)
  residual = BatchNormalization()(residual)

  # Block 2
  x = SeparableConv2D(128, (3, 3), padding='same', use_bias=False)(x)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)
  x = SeparableConv2D(128, (3, 3), padding='same', use_bias=False)(x)
  x = BatchNormalization()(x)

  # Block 2 Pool
  x = MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)
  x = layers.add([x, residual])
  residual = Conv2D(256, (1, 1), strides=(2, 2), padding='same', use_bias=False)(x)
  residual = BatchNormalization()(residual)

  # Block 3
  x = Activation('relu')(x)
  x = SeparableConv2D(256, (3, 3), padding='same', use_bias=False)(x)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)
  x = SeparableConv2D(256, (3, 3), padding='same', use_bias=False)(x)
  x = BatchNormalization()(x)

  # Block 3 Pool
  x = MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)
  x = layers.add([x, residual])
  residual = Conv2D(728, (1, 1), strides=(2, 2), padding='same', use_bias=False)(x)
  residual = BatchNormalization()(residual)

  # Block 4
  x = Activation('relu')(x)
  x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False)(x)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)
  x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False)(x)
  x = BatchNormalization()(x)
  x = MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)
  x = layers.add([x, residual])

  # Block 5 -> 12
  for i in range(8):
    residual = x
    x = Activation('relu')(x)
    x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False)(x)
    x = BatchNormalization()(x)
    x = layers.add([x, residual])

  residual = Conv2D(1024, (1, 1), strides=(2, 2), padding='same', use_bias=False)(x)
  residual = BatchNormalization()(residual)

  # Block 13
  x = Activation('relu')(x)
  x = SeparableConv2D(728, (3, 3), padding='same', use_bias=False)(x)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)
  x = SeparableConv2D(1024, (3, 3), padding='same', use_bias=False)(x)
  x = BatchNormalization()(x)

  # Block 13 Pool
  x = MaxPooling2D((3, 3), strides=(2, 2), padding='same')(x)
  x = layers.add([x, residual])

  # Block 14
  x = SeparableConv2D(1536, (3, 3), padding='same', use_bias=False)(x)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)

  # Block 14 part 2
  x = SeparableConv2D(2048, (3, 3), padding='same', use_bias=False)(x)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)

  model = Model(img_input, x, name='xception')
  weights = get_file('xception_weights_tf_dim_ordering_tf_kernels_notop.h5', url, cache_subdir='models')
  model.load_weights(weights)
  
  return model

from keras.utils.vis_utils import plot_model

def xception():
    base_model = create_base_model()
    base_model.trainable = False
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.2)(x)
    predictions = Dense(120, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    for layer in base_model.layers:
        layer.trainable = False

    model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
    # model.summary()
    plot_model(model, to_file='xception_model.png', show_shapes=True, show_layer_names=True)
    for i, layer in enumerate(model.layers):
        if i < 81:
            layer.trainable = False
        else:
            layer.trainable = True

    history = model.fit(train_ds, batch_size=32, epochs=10, validation_data=val_ds,verbose=1)
    return model

model = xception()

# save model
model.save("my_h5_model2.h5")
model.save_weights("weight_model2.h5")
test_ds = test_ds.map(preprocess)
results = model.evaluate(test_ds)

