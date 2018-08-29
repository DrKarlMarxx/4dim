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
#dataset['Bool. Tag']=[int(x&y) for (x,y) in zip(dataset.index.hour < 20,dataset.index.hour>8)]
#dataset['Bool. Tag']=dataset['Bool. Tag']-0.5
corr = dataset.corr()
fig, ax = plt.subplots()
cax=ax.matshow(abs(corr))
print(corr)
fig.colorbar(cax)
labels1 = list(corr.columns)
labels1[3]='Luftgeschw.'
plt.xticks(range(len(corr.columns)), labels1,rotation=30);
plt.yticks(range(len(corr.columns)), labels1);
plt.show()
exegon = dataset[['Regendauer','Windgeschwindigkeit vektoriell']]
#exegon['index1']=[int(x&y) for (x,y) in zip(exegon.index.hour < 20,exegon.index.hour>8)]
#exegon['index1']=exegon['index1']-0.5
dataset = dataset['PM10']
#exegon['Regendauer']=exegon['Regendauer']-num.mean(exegon['Regendauer'])
#exegon['Windgeschwindigkeit vektoriell']=exegon['Windgeschwindigkeit vektoriell']-num.mean(exegon['Windgeschwindigkeit vektoriell'])


dataset.plot()
plt.show()

ntrain = int(num.floor(len(dataset)*0.66))
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

model = ARIMA(train.diff(1)[1:],exog=exegon.values[2-1:ntrain-1], order=(2,0,1))
model_fit = model.fit(disp=0)
ar_coef = model_fit.arparams
print(model_fit.summary())
# plot residual errors
residuals = DataFrame(model_fit.resid)
ax = residuals.rolling(window=168).mean().plot()
plt.xlabel('Zeitschritt/Datum')
plt.ylabel('Gleitender Mittelwert der Residuen $[\mu g/m3]$')
ax.legend_.remove()
plt.ylim(-100,100)
plt.show()
ax = residuals.rolling(window=168).var().plot()
plt.ylim(0,100)
plt.xlabel('Zeitschritt/Datum')
plt.ylabel('Gleitende Varianz der Residuen $[\mu g/m3]$')
ax.legend_.remove()
plt.show()
print(residuals.describe())


plt.show()
#model = ARIMA(dataset.iloc[1:ntrain+ix].diff(1)[1:],exog=exegon.values[2:ntrain+ix], order=(5, 0, 1))


prediction24h = num.zeros((100,24))
measurement24h = num.zeros((100,24))
datetime24h = []
rain24h = num.zeros((100,24))
for ix in range(100):
	model = ARIMA(dataset.diff(1)[2:ntrain + ix], exog=exegon.values[2-2:ntrain + ix-2], order=(5, 0, 1))
	model_fit = model.fit(disp=0)
	prediction24h[ix, :]=test.values[ix]+num.cumsum(model_fit.predict(start=ntrain+ix-2, end = ntrain+ix+23-2,exog=exegon.values[ntrain-5-2+ix:ntrain+ix+24-2]).values)
	#prediction24h[ix, :] = model_fit.predict(start=ntrain + ix-2, end=ntrain + ix + 23-2,exog=exegon.values[ntrain-4+ix:ntrain+ix+24]).values
	measurement24h[ix,:] = test.iloc[ix:ix+24]
	rain24h[ix,:]=exegon.values[ntrain+ix:ntrain+ix+24,0]
	datetime24h.append(exegon.iloc[ntrain+ix:ntrain+ix+24,0].index)
	print(ix)

rmse24  = [num.sqrt(mean_squared_error(prediction24h[:,t], measurement24h[:,t])) for t in range(24)]

fig4 = plt.figure(4)
ax41 = fig4.add_subplot(111)
ax41.plot(rmse24)
ax41.set_xlabel('Prognoselänge [h]')
ax41.set_ylabel('Prognosenfehler (RMS) [-]')
plt.show()


fig2 = plt.figure(2)
ax1 = fig2.add_subplot(121)
line1 = ax1.plot(datetime24h[92].strftime('%H'),measurement24h[92], label='Messwert')
line2 = ax1.plot(datetime24h[92].strftime('%H'),prediction24h[92], label='Prognose')
ax1.set_xlabel('Prognosenzeitschritte [Uhrzeit]')
ax1.set_ylabel('Feinstaubwert $PM_{10}\ [\mu g/m3]$')
ax11 = ax1.twinx()
line3 = ax11.plot(datetime24h[92].strftime('%H'),rain24h[92],color='#2ca02c', label='Regendauer')
ax11.set_ylabel('[min]')
ax1.legend(loc=2)
ax11.legend(loc=1)
#ax1.legend((line1,line2,line3),("Messwert","Prognose","Regendauer"))
ax2 = fig2.add_subplot(122)
line1 = ax2.plot(datetime24h[9].strftime('%H'),measurement24h[9], label='Messwert')
line2 = ax2.plot(datetime24h[9].strftime('%H'),prediction24h[9], label='Prognose')
ax21 = ax2.twinx()
line3 = ax21.plot(datetime24h[9].strftime('%H'),rain24h[9],color='#2ca02c', label='Regendauer')
ax21.set_ylabel('[min]')
ax2.set_xlabel('Prognosenzeitschritte [Uhrzeit]')
ax2.set_ylabel('Feinstaubwert $PM_{10}\ [\mu g/m3]$')
ax2.legend(loc=2)
ax21.legend(loc=1)
#ax2.legend((line1,line2,line3),("Messwert","Prognose","Regendauer"))
plt.show()
