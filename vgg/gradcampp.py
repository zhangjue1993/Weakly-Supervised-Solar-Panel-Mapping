
# -*- coding: UTF-8 -*-
import tensorflow as tf
from vgg import vgg16
import os
import numpy as np
import cv2
from utils import *
import os
import imageio
os.environ["CUDA_VISIBLE_DEVICES"] = '0'
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:                   
        os.makedirs(path)  

classification_class = ['residential', 'back']
image_dir = '/scratch/po21/jz1585/Google-ACT-256/test/'
epoch = 30
batch_size = 64
lr = 1e-4
istrain = False
layername = 'conv4_3'
diro = '/scratch/po21/jz1585/Google-ACT-256/train-new1202/label-all/'
#result_dir = '/scratch/po21/jz1585/Google-Bris/test-conv/'#os.path.join(diro,layername)
result_dir = '/scratch/po21/jz1585/Google-ACT-256/test-conv/'
mkdir(result_dir)
print(result_dir)

image = tf.placeholder(tf.float32, [None, 256, 256, 3])
label = tf.placeholder(tf.float32, [None, 2])
sess = tf.Session()
vgg = vgg16(image, "vgg16.npy", sess)
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=vgg.fc3l, labels=label))
train_step = tf.train.GradientDescentOptimizer(learning_rate=lr).minimize(loss)
# train_step = tf.train.AdamOptimizer(0.01).minimize(loss)
accuracy = tf.reduce_mean(tf.cast(tf.equal(vgg.prediction, tf.argmax(label, 1)), tf.float32))

tf.summary.scalar('acc', accuracy)
tf.summary.scalar('loss', loss)
summary_step = tf.summary.merge_all()
summary_writer = tf.summary.FileWriter('./log')
saver = tf.train.Saver()
model_path = './model/'
kk = 0

with tf.Session() as sess:
    checkpoint = tf.train.get_checkpoint_state('./model/')

    if checkpoint and checkpoint.model_checkpoint_path:
        print('Restoring model...')

        sess.run(tf.global_variables_initializer())
        saver.restore(sess, checkpoint.model_checkpoint_path)

        print('Restoration complete.')
  
    error = 0
    image_num = len(os.listdir(image_dir))
    print(image_num)
    for i in range(1,image_num+3000):
        # print file_name
        if  os.path.exists(image_dir +'/'+'1-'+str(i)+'.png'): 
            image1 = imageio.imread(image_dir +'/'+'1-'+str(i)+'.png')
            image = np.expand_dims(image1, axis=0)
            prob = sess.run(vgg.probs, feed_dict={vgg.imgs: image})[0]
            preds = (np.argsort(prob)[::-1])[0:2]
            print('\n *******prob:', prob)
            pre_class = np.argmax(preds,axis=0)

            preds = (np.argsort(prob)[::-1])[0:2]
            print(preds)
            cam1 = grad_cam(image, vgg, sess, 0, layername, 2)
            imageio.imsave(result_dir + '/'+'1-'+str(i)+'.png', cam1)
            #misc.imsave(result_dir + '/original'+'1-'+str(i)+'.png', image1)
        if  os.path.exists(image_dir +'/'+'0-'+str(i)+'.png'):
            image1 = imageio.imread(image_dir +'/'+'0-'+str(i)+'.png')
            imageio.imsave(result_dir + '/'+'0-'+str(i)+'.png', image1*0)
        
        
        