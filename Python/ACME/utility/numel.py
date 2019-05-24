from .isscalar import *
from .size     import *
from functools import reduce

def numel(A):
    """
    Returns the number of elements contained in the given Tensor

    Parameters
    ----------
    A : Tensor
        a tensor/matrix
    Returns
    -------
    int
        the number of elements in the given tensor
    """

    s = size(A)
    if isscalar(s):
        return s
    return reduce((lambda a, b : a*b), s)
