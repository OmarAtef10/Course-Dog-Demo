import tensorflow as tf
import numpy as np
import transformers
import tensorflow_hub as hub

class DataGenerator(tf.keras.utils.Sequence):
  def __init__(
      self,
      sentence_pairs,
      labels,
      return_targets,
      shuffle,
      batch_size,
      tokenizer
  ):
    self.sentence_pairs = sentence_pairs.values.astype("str")
    self.labels = labels
    self.return_targets = return_targets
    self.shuffle = shuffle
    self.batch_size = batch_size
    self.indexes = np.arange(len(self.sentence_pairs))
    self.tokenizer = tokenizer
    if(self.shuffle): self.on_epoch()

  def __len__(self):
    return len(self.sentence_pairs) // self.batch_size

  def __getitem__(self, idx):
    indices = self.indexes[idx * self.batch_size : (idx + 1) * self.batch_size]
    sentence_pairs = self.sentence_pairs[indices]
    encoded_pairs = []
    for pair_ind in indices:
      encoded = self.tokenizer(self.sentence_pairs[pair_ind])
      # encoded = tf.reshape(encoded, (1, 512, 2))
      encoded_pairs.append(encoded)

    if(self.return_targets):
      labels = []
      for label_ind in indices:
        labels.append(self.labels[label_ind])
      labels = np.array(labels, dtype='int64')
      return np.array(encoded_pairs), labels
    else:
      return np.array(encoded_pairs)


  def on_epoch(self):
    if self.shuffle:
      np.random.RandomState(42).shuffle(self.indexes)
