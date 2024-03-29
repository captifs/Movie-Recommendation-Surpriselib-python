import numpy as np
import tensorflow as tf

class RBM(object):

    def __init__(self, visibleDimensions, epochs=20, hiddenDimensions=50, ratingValues=10, learningRate=0.001, batchSize=100):

        self.visibleDimensions = visibleDimensions
        self.epochs = epochs
        self.hiddenDimensions = hiddenDimensions
        self.ratingValues = ratingValues
        self.learningRate = learningRate
        self.batchSize = batchSize
        
                
    def Train(self, X):

        maxWeight = -4.0 * np.sqrt(6.0 / (self.hiddenDimensions + self.visibleDimensions))
        self.weights = tf.Variable(tf.random.uniform([self.visibleDimensions, self.hiddenDimensions], minval=-maxWeight, maxval=maxWeight), tf.float32, name="weights")
        self.hiddenBias = tf.Variable(tf.zeros([self.hiddenDimensions], tf.float32, name="hiddenBias"))
        self.visibleBias = tf.Variable(tf.zeros([self.visibleDimensions], tf.float32, name="visibleBias"))

        for epoch in range(self.epochs):
            
            trX = np.array(X)
            for i in range(0, trX.shape[0], self.batchSize):
                epochX = trX[i:i+self.batchSize]
                self.MakeGraph(epochX)

            print("Trained epoch ", epoch)


    def GetRecommendations(self, inputUser):
        
        feed = self.MakeHidden(inputUser)
        rec = self.MakeVisible(feed)
        return rec[0]       

    def MakeGraph(self, inputUser):
        
        hProb0 = tf.nn.sigmoid(tf.matmul(inputUser, self.weights) + self.hiddenBias)
        hSample = tf.nn.relu(tf.sign(hProb0 - tf.random.uniform(tf.shape(hProb0))))
        forward = tf.matmul(tf.transpose(inputUser), hSample)
        
        v = tf.matmul(hSample, tf.transpose(self.weights)) + self.visibleBias
 
        vMask = tf.sign(inputUser) 
        vMask3D = tf.reshape(vMask, [tf.shape(v)[0], -1, self.ratingValues]) 
        vMask3D = tf.reduce_max(vMask3D, axis=[2], keepdims=True) 
        
        v = tf.reshape(v, [tf.shape(v)[0], -1, self.ratingValues])
        vProb = tf.nn.softmax(v * vMask3D) 
        vProb = tf.reshape(vProb, [tf.shape(v)[0], -1]) 

        hProb1 = tf.nn.sigmoid(tf.matmul(vProb, self.weights) + self.hiddenBias)
        backward = tf.matmul(tf.transpose(vProb), hProb1)
    
        weightUpdate = self.weights.assign_add(self.learningRate * (forward - backward))
        hiddenBiasUpdate = self.hiddenBias.assign_add(self.learningRate * tf.reduce_mean(hProb0 - hProb1, 0))
        visibleBiasUpdate = self.visibleBias.assign_add(self.learningRate * tf.reduce_mean(inputUser - vProb, 0))

        self.update = [weightUpdate, hiddenBiasUpdate, visibleBiasUpdate]
        
    def MakeHidden(self, inputUser):
        hidden = tf.nn.sigmoid(tf.matmul(inputUser, self.weights) + self.hiddenBias)
        self.MakeGraph(inputUser)
        return hidden
    
    def MakeVisible(self, feed):
        visible = tf.nn.sigmoid(tf.matmul(feed, tf.transpose(self.weights)) + self.visibleBias)
        #self.MakeGraph(feed)
        return visible
