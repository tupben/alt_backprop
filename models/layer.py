import numpy as np
from skimage.util.shape import view_as_blocks
import skimage
from receptive_field import ReceptiveField


class Layer(object):

    def __init__(self, receptive_field , input_dims):
        """ A layer contains one receptive field that is slid over the input image. This is similar to a filter in a
        convolution neural network.
        """
        assert input_dims[0] == input_dims[1]
        self.input_dims = input_dims
        self.receptive_field = receptive_field

        self.output_layer = None
        self.input_layer = None

    def accept_input(self, signal, learn=True):
        """ Takes an input and learns it, passes it to the next layer"""

        if np.shape(signal)[0] != np.shape(signal)[1]:
            raise Exception('Input signal must be square.')

        if np.shape(signal) != self.input_dims:
            raise Exception('Input signal is of the wrong dimensionality.')

        # Adds padding to the image
        padding_needed = int(len(signal[0]) % self.receptive_field.neuron_shape[0])
        signal = skimage.util.pad(signal, [padding_needed, padding_needed], 'minimum')

        # Split the input up into patches
        patches = view_as_blocks(signal, self.receptive_field.neuron_shape)
        # WARNING: This IS PROBABLY be wrong
        patches = patches.reshape(-1, self.receptive_field.neuron_shape[0], self.receptive_field.neuron_shape[0])

        # Send those patches to the receptive field, and get the neuron that was most strongly excited
        # for each patch
        excited_neurons = []
        for patch in patches:
            cneuron = self.receptive_field.accept_input(patch, learn=learn)
            excited_neurons.append(cneuron)

        if self.output_layer:
            # Now we know the neuron that was excited for each receptive field in the input image
            # Create a new 'image' where each pixel contains a 2d position value, this value corresponds to the
            # position of the excited neuron.
            positions = [cneuron.position for cneuron in excited_neurons]
            positions = np.reshape(positions, self.receptive_field.shape)
            self.output_layer.accept_input(positions, learn=learn)

            # WARNING!!!!
            # TODO  Check that the reshape is working in the correct order

    def visualize(self, upstream=None):
        if self.input_layer is None:
            self.receptive_field.visualize()
        if self.output_layer:
            self.output_layer.visualize(self.receptive_field)


    def set_output_layer(layer):
        self.output_layer = layer


    def set_input_layer(layer):
        self.input_layer = layer