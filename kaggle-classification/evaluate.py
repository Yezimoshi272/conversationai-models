import argparse
import numpy as np
import pandas as pd
from trainer import wikidata
import tensorflow as tf

# Name of the input words feature
WORDS_FEATURE = 'words'

# TODO: infer this from the saved model
MAX_DOCUMENT_LENGTH = 500

def predict(data, classifier):
    """
    Args:
      data: n x m array of features where n is the number of examples
            and m is the number of features.
      classifier: a SavedModelPredictor with an input tensor 'input' that
                  expects as input a list of tf.train.Example's.

    Returns:
      scores: a n x num_classes array of scores for each each class
    """
    model_inputs = []
    for d in data[0:100]:
        input = tf.train.Example(
            features=tf.train.Features(
                feature={
                    WORDS_FEATURE: tf.train.Feature(
                        int64_list=tf.train.Int64List(value=d)
                    )
                }
            )
        )

        model_inputs.append(input.SerializeToString())

    output_dict = classifier({'inputs': model_inputs})
    scores = output_dict['scores']

    return scores

def load_model(session, model_dir):
    """Loads SavedModel model and returns classifier."""
    tf.saved_model.loader.load(
        session, [tf.saved_model.tag_constants.SERVING], model_dir)

    classifier = tf.contrib.predictor.from_saved_model(model_dir)

    return classifier

def main():

    with tf.Session(graph=tf.Graph()) as sess:
        classifier = load_model(sess, FLAGS.model_dir)

    # load test data
    data = wikidata.WikiData(
        data_path=FLAGS.test_data, max_document_length=MAX_DOCUMENT_LENGTH,
        test_mode=True, model_dir=FLAGS.model_dir)

    # evaluate model on data
    scores = predict(data.x_test, classifier)

    for i in range(len(scores)):
        print scores[i][0], data.x_test_text[i]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test_data', help='Path to data to evaluate on.', type=str)
    parser.add_argument('--model_dir', help='Path to directory with TF model.', type=str)

    FLAGS, unparsed = parser.parse_known_args()

    main()
