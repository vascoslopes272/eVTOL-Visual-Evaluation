import numpy as np

from lib.association import adjusted_residuals


def test_adjusted_residuals_equal_statsmodels():
    """lib.association.adjusted_residuals equals statsmodels' Table.standardized_resids."""
    import statsmodels.api as sm
    t = np.array([[366, 173, 48, 9, 29], [426, 225, 365, 86, 127]])
    assert np.allclose(adjusted_residuals(t), sm.stats.Table(t).standardized_resids, rtol=0, atol=1e-10)


def test_adjusted_residuals_2x2_square_is_chi2():
    """On a 2x2 table every adjusted residual squared equals the uncorrected chi-square."""
    from scipy.stats import chi2_contingency
    t = np.array([[30, 10], [20, 40]])
    chi2 = chi2_contingency(t, correction=False)[0]
    assert np.allclose(adjusted_residuals(t) ** 2, chi2)
