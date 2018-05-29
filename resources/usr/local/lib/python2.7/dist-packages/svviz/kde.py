#-------------------------------------------------------------------------------
#
#  Define classes for (uni/multi)-variate kernel density estimation.
#
#  Currently, only Gaussian kernels are implemented.
#
#  Written by: Robert Kern
#
#  Date: 2004-08-09
#
#  Modified: 2005-02-10 by Robert Kern.
#              Contributed to Scipy
#            2005-10-07 by Robert Kern.
#              Some fixes to match the new scipy_core
#
#  Copyright 2004-2005 by Enthought, Inc.
#
#-------------------------------------------------------------------------------



from numpy import atleast_2d, reshape, zeros, newaxis, dot, exp, pi, sqrt, power, sum, linalg
import numpy as np



class gaussian_kde(object):
    def __init__(self, dataset):
        self.dataset = atleast_2d(dataset)
        if not self.dataset.size > 1:
            raise ValueError("`dataset` input should have multiple elements.")

        self.d, self.n = self.dataset.shape
        self._compute_covariance()

    def evaluate(self, points):
        points = atleast_2d(points)

        d, m = points.shape
        if d != self.d:
            if d == 1 and m == self.d:
                # points was passed in as a row vector
                points = reshape(points, (self.d, 1))
                m = 1
            else:
                msg = "points have dimension %s, dataset has dimension %s" % (d,
                    self.d)
                raise ValueError(msg)

        result = zeros((m,), dtype=np.float)

        if m >= self.n:
            # there are more points than data, so loop over data
            for i in range(self.n):
                diff = self.dataset[:, i, newaxis] - points
                tdiff = dot(self.inv_cov, diff)
                energy = sum(diff*tdiff,axis=0) / 2.0
                result = result + exp(-energy)
        else:
            # loop over points
            for i in range(m):
                diff = self.dataset - points[:, i, newaxis]
                tdiff = dot(self.inv_cov, diff)
                energy = sum(diff * tdiff, axis=0) / 2.0
                result[i] = sum(exp(-energy), axis=0)

        result = result / self._norm_factor

        return result

    __call__ = evaluate


    def scotts_factor(self):
        return power(self.n, -1./(self.d+4))

    def _compute_covariance(self):
        self.factor = self.scotts_factor()
        # Cache covariance and inverse covariance of the data
        if not hasattr(self, '_data_inv_cov'):
            self._data_covariance = atleast_2d(np.cov(self.dataset, rowvar=1,
                                               bias=False))
            self._data_inv_cov = linalg.inv(self._data_covariance)

        self.covariance = self._data_covariance * self.factor**2
        self.inv_cov = self._data_inv_cov / self.factor**2
        self._norm_factor = sqrt(linalg.det(2*pi*self.covariance)) * self.n


if __name__ == '__main__':
    from biorpy import r
    from scipy import stats
    values = np.concatenate([np.random.normal(size=20), np.random.normal(loc=6, size=30)])

    kde = stats.gaussian_kde(values)
    x = np.linspace(-5,10, 50)
    y = kde(x)
    print(y)
    r.plot(x, y, type="l", col="red")


    kde2 = gaussian_kde(values)
    y2 = kde2(x)
    r.lines(x, y2, col="blue", lty=2)

    input("")



