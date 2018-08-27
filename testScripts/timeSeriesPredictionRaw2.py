import numpy
import matplotlib.pyplot as plt
from pandas import read_csv
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from scipy.ndimage.interpolation import shift

import numpy as np
import matplotlib.pyplot as plt
import pandas

# For 3d plots. This import is necessary to have 3D plotting below
from mpl_toolkits.mplot3d import Axes3D

# For statistics. Requires statsmodels 5.0 or more
from statsmodels.formula.api import ols
# Analysis of Variance (ANOVA) on linear models
from statsmodels.stats.anova import anova_lm

import numpy as num
# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return numpy.array(dataX), numpy.array(dataY)
# fix random seed for reproducibility
numpy.random.seed(7)
# load the dataset
dataset = read_csv('Duebendorf.csv', header=0, index_col=0)
dataset.fillna(0, inplace=True)
columns = dataset.columns.tolist()
newColumns = columns[1:]+columns[:1]
dataset = dataset[newColumns]


dataset = dataset['PM10']
dataset = dataset.values
dataset = dataset.astype('float32').reshape(-1, 1)
# normalize the dataset
scaler = MinMaxScaler(feature_range=(0, 1))
dataset = scaler.fit_transform(dataset)
# split into train and test sets
train_size = int(len(dataset) * 0.67)
test_size = len(dataset) - train_size-3
train, test = dataset[0:train_size,:], dataset[train_size:len(dataset)-3,:]
# reshape into X=t and Y=t+1
look_back = 48
trainX, trainY = create_dataset(train, look_back)
testX, testY = create_dataset(test, look_back)
# reshape input to be [samples, time steps, features]
trainX = numpy.reshape(trainX, (trainX.shape[0], trainX.shape[1], 1))
testX = numpy.reshape(testX, (testX.shape[0], testX.shape[1], 1))
# create and fit the LSTM network
batch_size = 1
model = Sequential()
model.add(LSTM(16, batch_input_shape=(batch_size, look_back, 1),return_sequences=True, stateful=True))
model.add(LSTM(16, batch_input_shape=(batch_size, look_back, 1), stateful=True))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
for i in range(5):
	model.fit(trainX, trainY, epochs=1, batch_size=batch_size, verbose=2, shuffle=False)
	model.reset_states()
# make predictions
trainPredict = model.predict(trainX, batch_size=batch_size)
model.reset_states()
testPredict = model.predict(testX, batch_size=batch_size)
# invert predictions
trainPredict = scaler.inverse_transform(trainPredict)
trainY = scaler.inverse_transform([trainY])
testPredict = scaler.inverse_transform(testPredict)
testY = scaler.inverse_transform([testY])
# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
print('Train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
print('Test Score: %.2f RMSE' % (testScore))
# shift train predictions for plotting
trainPredictPlot = numpy.empty_like(dataset)
trainPredictPlot[:, :] = numpy.nan
trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict
# shift test predictions for plotting
testPredictPlot = numpy.empty_like(dataset)
testPredictPlot[:, :] = numpy.nan
testPredictPlot[len(trainPredict)+(look_back*2)+1:len(dataset)-4, :] = testPredict
# plot baseline and predictions
plt.plot(scaler.inverse_transform(dataset))
plt.plot(trainPredictPlot)
plt.plot(testPredictPlot)
plt.show()


prediction24h = num.zeros((num.size(testY,1)-49,24))
measurement24h = num.zeros((num.size(testY,1)-49,24))
for ix in range(num.size(testY,1)-49):

    currentPredictionState = num.expand_dims(testX[ix],0)
    for t in range(24):

        prediction = model.predict(currentPredictionState)
        inv = scaler.inverse_transform(prediction[:])
        prediction24h[ix,t]=inv
        measurement24h[ix,t]=testY[0,ix+t]
        currentPredictionState[0,0:-1,0] =  currentPredictionState[0,1:,0]
        currentPredictionState[0,-1,0] = prediction
        #print(prediction24h[ix,t])
        #print(measurement24h[ix,t])
    if num.floor(ix/1000)==ix/1000:
        print(ix)


rmse24  = [num.sqrt(mean_squared_error(prediction24h[:,t], measurement24h[:,t])) for t in range(24)]

fig4 = plt.figure(4)
ax41 = fig4.add_subplot(111)
ax41.plot(rmse24)
plt.show()


fig2 = plt.figure(2)
ax1 = fig2.add_subplot(221)
ax1.plot(measurement24h[1], label='real')
ax1.plot(prediction24h[1], label='prediction')
ax1.legend()
ax2 = fig2.add_subplot(222)
ax2.plot(measurement24h[100], label='real')
ax2.plot(prediction24h[100], label='prediction')
ax2.legend()
ax3 = fig2.add_subplot(223)
ax3.plot(measurement24h[1000], label='real')
ax3.plot(prediction24h[1000], label='prediction')
ax3.legend()
ax4 = fig2.add_subplot(224)
ax4.plot(measurement24h[2500], label='real')
ax4.plot(prediction24h[2500], label='prediction')
ax4.legend()
plt.show()
