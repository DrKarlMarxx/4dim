import numpy
import matplotlib.pyplot as plt
from pandas import read_csv, DataFrame
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from scipy.ndimage.interpolation import shift
from pandas.plotting import autocorrelation_plot
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARIMA
import datetime
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
def parse(x):
	return datetime.datetime.strptime(x, '%d.%m.%Y %H:%M')
dataset = read_csv('AppenzellRaw.csv', header=0, index_col=0,date_parser=parse)
dataset.dropna( inplace=True)
columns = dataset.columns.tolist()
newColumns = columns[1:]+columns[:1]
dataset = dataset[newColumns]
exegon = dataset[['Regendauer','Globalstrahlung','Luftfeuchte relativ']]
dataset = dataset['PM10']



dataset.plot()
plt.show()

ntrain = int(num.floor(len(dataset)*0.6))
train = dataset.iloc[1:ntrain]
test = dataset.iloc[ntrain:]
#train.diff()[1:]
ac = plot_acf(train.diff(1)[1:],lags=48)
plt.xlabel('Zeitschrittabstand  [-]')
plt.ylabel('[-]')
plt.show()

ac = plot_pacf(train.diff(1)[1:],lags=48)
plt.xlabel('Zeitschrittabstand [-]')
plt.ylabel('[-]')

plt.show()

model = ARIMA(train.iloc[1:],exog=exegon.values[2+1:ntrain+1], order=(2,0,1))
model_fit = model.fit(disp=0)
ar_coef = model_fit.arparams
print(model_fit.summary())
# plot residual errors
residuals = DataFrame(model_fit.resid)
ax = residuals.rolling(window=168).mean().plot()
plt.xlabel('Zeitschritt [h]')
plt.ylabel('Gleitender Mittelwert der Residuen $[\mu g/m3]$')
ax.legend_.remove()
plt.ylim(-100,100)
plt.show()
ax = residuals.rolling(window=168).var().plot()
plt.ylim(0,100)
plt.xlabel('Zeitschritt [h]')
plt.ylabel('Gleitende Varianz der Residuen $[\mu g/m3]$')
ax.legend_.remove()
plt.show()
print(residuals.describe())


plt.show()
#model = ARIMA(dataset.iloc[1:ntrain+ix].diff(1)[1:],exog=exegon.values[2:ntrain+ix], order=(5, 0, 1))


prediction24h = num.zeros((100,24))
measurement24h = num.zeros((100,24))
for ix in range(10):
	model = ARIMA(dataset.iloc[2:ntrain + ix], exog=exegon.values[2:ntrain + ix], order=(2, 0, 1))
	model_fit = model.fit(disp=0,solver = 'bfgs',tol=1e-08)
	#prediction24h[ix, :]=test.values[ix]+num.cumsum(model_fit.predict(start=ntrain+ix-2, end = ntrain+ix+23-2,exog=exegon.values[ntrain-2+ix:ntrain+ix+24]).values)
	prediction24h[ix, :] = model_fit.predict(start=ntrain + ix-2, end=ntrain + ix + 23-2,exog=exegon.values[ntrain-4+ix:ntrain+ix+24]).values
	measurement24h[ix,:] = test.values[ix:ix+24]


rmse24  = [num.sqrt(mean_squared_error(prediction24h[:,t], measurement24h[:,t])) for t in range(24)]

fig4 = plt.figure(4)
ax41 = fig4.add_subplot(111)
ax41.plot(rmse24)
ax41.set_xlabel('Prognoselänge [h]')
ax41.set_ylabel('Prognosenfehler (RMS) [-]')
plt.show()


fig2 = plt.figure(2)
ax1 = fig2.add_subplot(211)
ax1.plot(measurement24h[0], label='Messwert')
ax1.plot(prediction24h[0], label='Prognose')
ax1.set_xlabel('Prognosenlänge [h]')
ax1.set_ylabel('Feinstaubwert $PM_{10}\ [\mu g/m3]$')
ax1.legend()
ax2 = fig2.add_subplot(212)
ax2.plot(measurement24h[9], label='Messwert')
ax2.plot(prediction24h[9], label='Prognose')
ax2.set_xlabel('Prognosenlänge [h]')
ax2.set_ylabel('Feinstaubwert $PM_{10}\ [\mu g/m3]$')
ax2.legend()
plt.show()
