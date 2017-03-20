"""
This training procedure will train a network from scratch using raw data from
the dataset, and save the checkpoints.
"""
import numpy as np
import os
import tensorflow as tf
import utils as u
import models as m

from utils import ensure_dir_exists

MODEL_META = 'summaries/hinton1200_mnist/checkpoint/hinton1200-8000.meta'
MODEL_CHECKPOINT = 'summaries/hinton1200_mnist/checkpoint/hinton1200-8000'

def merge_summary_list(summary_list, do_print=False):
    summary_dict = {}

    for summary in summary_list:
        summary_proto = tf.Summary()
        summary_proto.ParseFromString(summary)

        for val in summary_proto.value:
            if val.tag not in summary_dict:
                summary_dict[val.tag] = []
            summary_dict[val.tag].append(val.simple_value)

    # get mean of each tag
    for k, v in summary_dict.items():
        summary_dict[k] = np.mean(v)

    if do_print:
        print(summary_dict)

    # create final Summary with mean of values
    final_summary = tf.Summary()
    final_summary.ParseFromString(summary_list[0])

    for i, val in enumerate(final_summary.value):
        final_summary.value[i].simple_value = summary_dict[val.tag]

    return final_summary

def run(sess, f, data, placeholders, train_step, summary_op):
    inp, labels, keep_inp, keep, temp, labels_temp = placeholders
    # train graph from scratch, save checkpoints every so often, eval, do summaries, etc.

    saver = tf.train.Saver(tf.global_variables())

    summary_dir = os.path.join(f.summary_folder, f.run_name)
    train_writer = tf.summary.FileWriter(os.path.join(summary_dir, 'train'), sess.graph)
    trainbatch_writer = tf.summary.FileWriter(os.path.join(summary_dir, 'train_batch'), sess.graph)
    test_writer = tf.summary.FileWriter(os.path.join(summary_dir, 'test'), sess.graph)

    with sess.as_default():
        global_step = 0

        for i in range(f.epochs):
            print('Epoch: {}'.format(i))
            for batch_x, batch_y in data.train_bottlenecks_epoch_in_batches(f.train_batch_size):
                summary, _ = sess.run([summary_op, train_step],
                        feed_dict={inp: batch_x, #labels: batch_y,
                            'inputs': batch_x,
                            keep_inp: 1.0, keep: 0.5,
                            temp: 8.0, labels_temp: 8.0})

                trainbatch_writer.add_summary(summary, global_step)

                if global_step % f.eval_interval == 0:
                    # eval test
                    summaries = []
                    for test_batch_x, test_batch_y in data.test_epoch_in_batches(f.test_batch_size):
                        summary = sess.run(summary_op,
                                feed_dict={inp: test_batch_x, #labels: test_batch_y,
                                    'inputs': batch_x,
                                    keep_inp: 1.0, keep: 1.0,
                                    temp: 1.0, labels_temp: 1.0})
                        summaries.append(summary)
                    test_writer.add_summary(merge_summary_list(summaries, True), global_step)

                    # eval train
                    summaries = []
                    for train_batch_x, train_batch_y in data.train_epoch_in_batches(f.train_batch_size):
                        summary = sess.run(summary_op,
                                feed_dict={inp: train_batch_x, #labels: train_batch_y,
                                    'inputs': batch_x,
                                    keep_inp: 1.0, keep: 1.0,
                                    temp: 1.0, labels_temp: 1.0})
                        summaries.append(summary)
                    train_writer.add_summary(merge_summary_list(summaries, True), global_step)

                global_step += 1

                if global_step % f.checkpoint_interval == 0:
                    checkpoint_dir = os.path.join(summary_dir, 'checkpoint/')
                    ensure_dir_exists(checkpoint_dir)
                    checkpoint_file = os.path.join(checkpoint_dir, f.model)
                    saver.save(sess, checkpoint_file, global_step=global_step)

def create_placeholders(input_size, output_size, optionals):
    #  keep_inp, keep, temp, labels_temp = optionals

    with tf.Session() as sess:
        new_saver = tf.train.import_meta_graph(MODEL_META)
        new_saver.restore(sess, MODEL_CHECKPOINT)
        print(new_saver.to_proto())
        #  print(tf.get_collection(tf.GraphKeys.VARIABLES))
        #  inp = tf.get_collection('inputs')[0]
        print(tf.get_collection('opt'))
        out = tf.get_collection('outputs')[0]

        keep_inp = tf.get_collection('keep_prob_input')[0]
        keep = tf.get_collection('keep_prob')[0]
        temp = tf.get_collection('temp')[0]
        #  labels_temp = tf.get_collection('labels_temp')[0]

    with tf.variable_scope('labels_sftmx'):
        labels = tf.nn.softmax(out)

    return inp, labels, keep_inp, keep, temp