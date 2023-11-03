from rest_framework.views import APIView
from rest_framework.response import Response
import yfinance as yf
import re
from .models import Currency as CurrencyModel, History as HistoryModel

class Currency(APIView):
    def get(self, request, currency = "", period = "1mo", sort="asc"):
        """Gets the currency rate

        Args:
            request (_type_): _description_
            currency (str, optional): Abbreviation of currency. Should be like EURUSD=X format. Defaults to "".
            period (str, optional): Defaults to "1mo".
            sort (str, optional): Defaults to "asc".

        Returns:
            list: all currencies if there is no currency parameter or history of currency rates
        """
        if currency == "":
            return Response(CurrencyModel.objects.all().values(), content_type='application/json')
        
        if not self._only_currencies_validator(currency):
            # raise Exception("Invalid currency abbreviation")
            return Response(
                "Invalid currency abbreviation. Currency format should be like EURUSD=X or JPY=X", 
                content_type='application/json', 
                status=400)        
        
        # try get currency from external db
        try:
            ticker = yf.Ticker(currency)
            hist = ticker.history(period=period)
        except:
            hist = None
            
        queryset = CurrencyModel.objects.filter(abbr=currency)
        
        # when cannot get currency from external db, try get it from internal db
        if hist is None:
            if queryset.exists():
                hist = HistoryModel.objects.filter(currency=queryset[0])
                if hist.exists():
                    hist = hist.values()
                else:
                    hist = None
            else:
                hist = None
                
            
            res = self.format_response(hist, sort)
            return Response(res, content_type='application/json')
        
        # when currency is in external db, save it to internal db
        if not hist.empty:
            last_rate = hist['Close'][-1:].values[0]
            
            # if there is already a currency with the same abbreviation, update its rate
            if queryset.exists():
                queryset.update(rate=last_rate)
                self.history_update(hist, queryset[0])
                res = self.format_response(hist, sort)
                return Response(res, content_type='application/json')
            
            # if there is no currency with the same abbreviation, 
            # create a new one and create its history
            cm = CurrencyModel(abbr=currency, rate=last_rate)
            cm.save()
            self.history_update(hist, queryset[0])
        
        res = self.format_response(hist, sort)
        return Response(res, content_type='application/json')
    
    def format_response(self, hist, sort):
        """Formats response to json format with sort applied."""
        sorted_hist = self.sort_history(hist, sort)
        return self.format_currecy_json(sorted_hist)

    def history_update(self, hist, currency_model):
        """Genetaror function for updating history model

        Args:
            currency_model (_type_): currency model
            hist (_type_): history of currency rates

        Returns:
            Void
        """
        for index, row in hist.iterrows():
            history_model = HistoryModel.objects.filter(date=index, currency=currency_model)
            if not history_model.exists():
                hm = HistoryModel(
                    currency = currency_model, 
                    date     = index, 
                    open     = row['Open'], 
                    high     = row['High'], 
                    low      = row['Low'], 
                    close    = row['Close'], 
                    volume   = row['Volume'])
                hm.save()
                
    def load_all_basic_currencies(self):
        """Loads all basic yahoo currencies into app database. \n
        Function for tests purposes, not really used in application."""
        basic_currencies = [
            "EURUSD=X",
            "JPY=X",
            "GBPUSD=X",
            "AUDUSD=X",
            "NZDUSD=X",
            "EURJPY=X",
            "GBPJPY=X",
            "EURGBP=X",
            "EURCAD=X",
            "EURSEK=X",
            "EURCHF=X",
            "EURHUF=X",
            "EURJPY=X",
            "CNY=X",
            "HKD=X",
            "SGD=X",
            "INR=X",
            "MXN=X",
            "PHP=X",
            "IDR=X",
            "THB=X",
            "MYR=X",
            "ZAR=X",
            "RUB=X"
            ]
        for currency in basic_currencies:
            self.get(None, currency)

    def format_currecy_json(self, history):
        """Formats currency history to json format with date as key"""
        history_dict = {}
        
        for h in history.iterrows():
            history_dict[h[0].strftime("%Y-%m-%d")] = {
                "open":         h[1]['Open'],
                "high":         h[1]['High'],
                "low":          h[1]['Low'],
                "close":        h[1]['Close'],
                "volume":       h[1]['Volume'],
                "dividends":    h[1]['Dividends'],
                "stock_splits": h[1]['Stock Splits']
            }
            
        return history_dict
    
    def sort_history(self, history, sort):
        """Sorts history by date"""
        if sort == "asc":
            return history
        elif sort == "desc":
            return history[::-1]
        else:
            return Response(
                "Invalid sort parameter. Sort parameter should be asc or desc", 
                content_type='application/json', 
                status=400)

    def _only_currencies_validator(self, currency):
        """Checks if abbr is a valid currency."""
        if re.search("^[A-Z]{6}\=X$", currency) or re.search("^[A-Z]{3}\=X$", currency):
            return True
        return False
        
