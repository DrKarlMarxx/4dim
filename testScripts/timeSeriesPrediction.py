from pandas import read_csv, DataFrame, concat
from datetime import datetime
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from keras.models import Sequential
from sklearn.metrics import mean_squared_error
from keras.layers import LSTM, Dense
from numpy import concatenate,sqrt

from matplotlib import pyplot
# convert series to supervised learning
def series_to_supervised(data, n_in=1, n_out=1,predict = '' ,dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.iloc[:,:-1].shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars-1)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars-1)]
    for i in range(0, n_out):
        cols.append(df.iloc[:,-1].shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in [n_vars-1]]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in [n_vars-1]]


    # put it all together
    agg = concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg


# load dataset
dataset = read_csv('pollution.csv', header=0, index_col=0)
columns = dataset.columns.tolist()
newColumns = columns[1:]+columns[:1]
dataset = dataset[newColumns]
values1 = dataset.values
# ensure all data is float
values1 = values1.astype('float32')
# normalize features

# frame as supervised learning
reframed = series_to_supervised(values1, 6, 24)
# drop columns we don't want to predict
#reframed.drop(reframed.columns[[9, 10, 11, 12, 13, 14, 15]], axis=1, inplace=True)
scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(reframed)
# print(reframed.head())



# split into train and test sets
values = scaled
n_train_hours = 365 * 24
train = values[:n_train_hours, :]
test = values[n_train_hours:, :]
# split into input and outputs
train_X, train_y = train[:, :-24], train[:, -24:]
test_X, test_y = test[:, :-24], test[:, -24:]
# reshape input to be 3D [samples, timesteps, features]
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

# design network
model = Sequential()
model.add(LSTM(32, input_shape=(train_X.shape[1], train_X.shape[2]),return_sequences=True))
model.add(LSTM(32))
model.add(Dense(24))
model.compile(loss='mae', optimizer='adam')
# fit network
history = model.fit(train_X, train_y, epochs=200, validation_data=(test_X, test_y), verbose=2, shuffle=False)
# plot history
pyplot.plot(history.history['loss'], label='train')
pyplot.plot(history.history['val_loss'], label='test')
pyplot.legend()
pyplot.show()


# make a prediction
yhat = model.predict(test_X)
test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
# invert scaling for forecast
inv_yhat = concatenate((test_X[:, :],yhat), axis=1)
inv_yhat = scaler.inverse_transform(inv_yhat)
inv_yhat = inv_yhat[:,-24:]
# invert scaling for actual
test_y = test_y.reshape((len(test_y), 24))
inv_y = concatenate((test_X[:, :],test_y), axis=1)
inv_y = scaler.inverse_transform(inv_y)
inv_y = inv_y[:,-24:]
# calculate RMSE
rmse = sqrt(mean_squared_error(inv_y.flatten(), inv_yhat.flatten()))

fig2 = pyplot.figure(2)
ax1 = fig2.add_subplot(221)
ax1.plot(inv_y[1], label='real')
ax1.plot(inv_yhat[1], label='prediction')
ax1.legend()
ax2 = fig2.add_subplot(222)
ax2.plot(inv_y[100], label='real')
ax2.plot(inv_yhat[100], label='prediction')
ax2.legend()
ax3 = fig2.add_subplot(223)
ax3.plot(inv_y[1000], label='real')
ax3.plot(inv_yhat[1000], label='prediction')
ax3.legend()
ax4 = fig2.add_subplot(224)
ax4.plot(inv_y[10000], label='real')
ax4.plot(inv_yhat[10000], label='prediction')
ax4.legend()
pyplot.show()
print('Test RMSE: %.3f' % rmse)