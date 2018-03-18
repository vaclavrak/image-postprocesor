"""

define dimension for any graphite request

"""

__author__ = 'rak'


class DimensionBuilder:
    _base_dimension = None
    _last_make = None
    _dim_builder = []

    def __init__(self):
        self._base_dimension = None
        self._dim_builder = []

    def set_dimension(self, dim: str) -> object:
        self._base_dimension = dim
        return self

    def sumSeries(self):
        return self.sum

    def sum(self) -> object:
        """
        sum of current dimension
        :return: self
        """
        self._dim_builder.append("sum(%(dim)s)")
        return self

    def summarize(self, intervalString, func='sum', alignToFrom=False):
        """
        Summarize the data into interval buckets of a certain size.
        :return: self
        """
        self._dim_builder.append("summarize(%%(dim)s,'%s','%s',%r)" % (intervalString, func, alignToFrom))
        return self

    def nPercentile(self, n_percentile):
        """
        nPercentile on metric
        :return: self
        """
        self._dim_builder.append("nPercentile(%%(dim)s,%d)" % n_percentile)
        return self

    def transformNull(self, replace_null_with=0):
        """
        transformNull None to Number
        :return: self
        """
        if replace_null_with == 0:
            self._dim_builder.append("transformNull(%(dim)s)")
        else:
            self._dim_builder.append("transformNull(%%(dim)s,%f)" % replace_null_with)
        return self

    def divByDimension(self, dimension):
        """
        divide by dimension
        :return: self
        """
        self._dim_builder.append("divideSeries(%%(dim)s,%s)" % dimension.make())
        return self

    def keepLastValue(self, points=0):
        """
        keep last value
        :return: self
        """
        if points > 0:
            self._dim_builder.append("keepLastValue(%%(dim)s,%d)" % points)
        else:
            self._dim_builder.append("keepLastValue(%%(dim)s)")
        return self

    def transformNull(self, value=0):
        """
        transform nulls
        :return: self
        """
        self._dim_builder.append("transformNull(%%(dim)s,%f)" % value)
        return self

    def __str__(self):
        return self._last_make

    def url_encode(self):
        return self._last_make

    def make(self, current_dim=None):
        """
        make graphite dimension according rules
        :return: self
        """
        self._last_make = None
        if current_dim is None:
            current_dim = self._base_dimension

        for fnc in self._dim_builder:
            current_dim = fnc % {"dim": current_dim}
        self._last_make = current_dim
        return self
