%%writefile StreamLitStockApp.py
import streamlit as st
import datetime as dt
from dateutil.relativedelta import relativedelta # to add days or years
import investpy
from fbprophet import Prophet
from fbprophet.plot import plot_plotly
from plotly import graph_objs as go
from fbprophet.diagnostics import cross_validation, performance_metrics
format = 'MMM DD, YYYY'  # format output
st.title("Time Series Analysis")

form = st.sidebar.form(key='Time-Series-Analysis')

dfStockName = investpy.get_stocks_overview(country="United Kingdom" 
                                          ,as_json=False
                                          ,n_results=1000
                                          )
selectedStockName = form.selectbox('Select the Stock Name ',list(dict.fromkeys(dfStockName['name'].tolist())))
startDate  = dt.date(year=2011,month=1,day=1) #-relativedelta(years=5)
endDate    = dt.datetime.now().date()  #-relativedelta(years=5)
maxDays    = endDate-startDate
#dateSlider = form.slider('Select date', min_value=startDate, value=endDate ,max_value=endDate, format=format)
values     = form.slider("Select date", startDate, endDate, (startDate, endDate), format=format)
#st.write('Values:', values[0])
noOfPeriods = form.slider("Number of Days ",1,1000)

submit     = form.form_submit_button('Submit')
selectedStockName = str(selectedStockName)
#FromDate = startDate.strftime('%d-%m-%Y')
#toDate   = dateSlider.strftime('%d-%m-%Y')
FromDate = values[0].strftime('%d/%m/%Y')
toDate   = values[1].strftime('%d/%m/%Y')
stockSymbol = dfStockName.loc[dfStockName['name'] == selectedStockName]['symbol'].item()

@st.cache
def loadData(pStockName,pSD,pED):
  #st.text_input(" Stock Symbol ",stockSymbol)
  #st.text_input(" SD ",startDate.strftime('%d/%m/%Y'))
  #st.text_input(" ED ",(dateSlider.strftime('%d/%m/%Y')))
  stockData = investpy.get_stock_historical_data(stock     = pStockName
                                                ,country   = 'United Kingdom'
                                                ,from_date = pSD 
                                                ,to_date   = pED 
                                                )
  
  return stockData
 





 
if submit:
    col1, col2, col3  = st.columns(3)
    col1.metric("Stock Name ", selectedStockName)
    col2.metric("From Date ", FromDate)
    col3.metric("To Date ", toDate)
    #col4.metric("Periods ",str(yearPrediction))
    dataLoadState = st.text("Data Loading ....")
     
    #df = loadData(stockSymbol,startDate.strftime('%d/%m/%Y'),dateSlider.strftime('%d/%m/%Y'))
    df = loadData(stockSymbol,values[0].strftime('%d/%m/%Y'),values[1].strftime('%d/%m/%Y'))
    #df['Date'] = df.index
    dataLoadState.text("Loading Data Done ..")

    #st.write(f'Selected Stock is  {selectedStockName}')
    #st.write(f'Start Date is      {dt.date.strftime(startDate, "%d/%m/%Y")}')
    #st.write(f'End  Date is       {dt.date.strftime(dateSlider, "%d/%m/%Y")}')

    st.subheader("Raw Data")
    df
    st.subheader("Chart")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y = df['Open'], name ='Open'))
    fig.add_trace(go.Scatter(x=df.index, y = df['Close'], name ='Close'))
    fig.layout.update(title_text='Time Series Data',xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

    st.subheader("Chart Candle Stick")
    fig1 = go.Figure(data = [go.Candlestick(x=df.index
                                           ,open  = df['Open']
                                           ,high  = df['High']
                                           ,low   = df['Low']
                                           ,close = df['Close']
                                           ,name  = selectedStockName
                                           )
                            ]
                    )
    fig1.update_xaxes(type='category')
    fig1.update_layout(height=600)
    st.plotly_chart(fig1,use_container_width=True)



    df['Date'] = df.index
    train_df = df[['Date','Close']]
    train_df = train_df.rename(columns={"Date":"ds","Close":"y"})
    m = Prophet()
    m.fit(train_df)
    future = m.make_future_dataframe(periods=noOfPeriods)
    forecast = m.predict(future)
    st.subheader("Time Series Forecast Data")
    st.write('ds -> forecast date')
    st.write('yhat -> forecast value for the given date')
    st.write('yhat_lower -> lower forecast boundary for the given date')
    st.write('yhat_upper -> upper forecast boundary for the given date')
     
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()


    st.write("Forecast Graph")
    fig2 = plot_plotly(m,forecast)
    st.plotly_chart(fig2)
    
    st.write("Forecast Components")
    fig3 = m.plot_components(forecast)
    st.write(fig3)

    #st.write("Performing the Cross Validation")
    #df_cv = cross_validation(m, horizon='90 days')
    #df_p = performance_metrics(df_cv)
    #df_p.head(5)
