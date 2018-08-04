class FourDigitYearConverter:
    regex = '([0-9]{1,}&)*[0-9]{1,}'

    def to_python(self, value):
        valueList = value.split('&')
        return [int(d) for d in valueList]

    def to_url(self, value):
        return "&".join(value)