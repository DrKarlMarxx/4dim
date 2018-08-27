from math import sqrt
from numpy import concatenate
from matplotlib import pyplot
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers.recurrent import LSTM
import numpy as num
import matplotlib.pyplot as plt

# convert series to supervised learning
def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
    # put it all together
    agg = concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg


# load dataset
dataset = read_csv('AppenzellRaw.csv', header=0, index_col=0)
dataset.fillna(0, inplace=True)
columns = dataset.columns.tolist()
newColumns = columns[1:]+columns[:1]
dataset = dataset[newColumns]
values = dataset.values

# ensure all data is float
values = values.astype('float32')
# normalize features
scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)
# frame as supervised learning
reframed = series_to_supervised(scaled, 1, 1)
# drop columns we don't want to predict

print(reframed.head())

# split into train and test sets
values = reframed.values
n_train_hours = 364 * 16
train = values[:n_train_hours, :]
test = values[n_train_hours:-8, :]
# split into input and outputs
train_X, train_y = train[:, :-1], train[:, -1]
test_X, test_y = test[:, :-1], test[:, -1]
# reshape input to be 3D [samples, timesteps, features]
train_X = train_X.reshape((train_X.shape[0],1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0],1, test_X.shape[1]))
print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

# design network
model = Sequential()
"""
model.add(LSTM(64, input_shape=(train_X.shape[1], train_X.shape[2]),return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(64, input_shape=(train_X.shape[1], train_X.shape[2]),return_sequences=True))
model.add(LSTM(64, input_shape=(train_X.shape[1], train_X.shape[2])))
"""
#model.add(LSTM(64, input_shape=(train_X.shape[1], train_X.shape[2]), batch_size=32,return_sequences=True,stateful=False))
model.add(LSTM(64, input_shape=(train_X.shape[1], train_X.shape[2]), batch_size=32,stateful=True))
model.add(Dense(1))
model.compile(loss='mse', optimizer='rmsprop')
# fit network
history = model.fit(train_X, train_y, epochs=50, batch_size=32, validation_data=(test_X, test_y), verbose=2,
                    shuffle=True)
# plot history
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()

# make a prediction
yhat = model.predict(test_X)
test_Xrs = test_X.reshape((test_X.shape[0], test_X.shape[2]))
# invert scaling for forecast
inv_yhat = concatenate((test_Xrs[:, :6],yhat), axis=1)
inv_yhat = scaler.inverse_transform(inv_yhat)
inv_yhat = inv_yhat[:, 6]
# invert scaling for actual
test_y = test_y.reshape((len(test_y), 1))
inv_y = concatenate(( test_Xrs[:, :6],test_y), axis=1)
inv = scaler.inverse_transform(inv_y)
inv_y = inv[:, 6]
inv_x = inv[:,0:6]

# calculate RMSE
rmse = sqrt(mean_squared_error(inv_y, inv_yhat))
print('Test RMSE: %.3f' % rmse)
fig2 = pyplot.figure(2)
ax1 = fig2.add_subplot(221)
ax1.plot(inv_y, label='real')
ax1.plot(inv_yhat, label='prediction')
ax1.plot(inv_x[:,4],label='rain')

ax1.legend()
ax2 = fig2.add_subplot(223)
ax2.plot(inv_x[:,4],label='rain')
#ax2.set_xlim([0,144])
ax3 = fig2.add_subplot(222)
ax3.plot(inv_y[1:]-inv_y[0:-1],inv_x[1:,4],'.',label='rain')
plt.show()

prediction24h = num.zeros((len(test_y)-25,24))
measurement24h = num.zeros((len(test_y)-25,24))
for ix in range(32,len(test_y)-25):

    currentPredictionState = test_X[ix-31:ix+1]
    cNew = currentPredictionState[:]
    for t in range(24):

        prediction = model.predict(cNew)
        inv = scaler.inverse_transform(concatenate((test_Xrs[ix+t-31:ix+t+1,:6],prediction[:]),axis=1))
        prediction24h[ix,t]=inv[-1,6]
        measurement24h[ix,t]=inv_y[ix+t]
        currentPredictionState = test_X[ix+t-31+1:ix+t+2]
        cNew = currentPredictionState[:]
        cNew[-1,0,6] = prediction[-1]
        print(prediction24h[ix,0])
        print(measurement24h[ix,0])
    if num.floor(ix/1000)==ix/1000:
        print(ix)


rmse24  = [sqrt(mean_squared_error(prediction24h[:,t], measurement24h[:,t])) for t in range(24)]

fig4 = plt.figure(4)
ax41 = fig4.add_subplot(111)
ax41.plot(rmse24)



fig2 = pyplot.figure(2)
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
pyplot.show()

plt.show()