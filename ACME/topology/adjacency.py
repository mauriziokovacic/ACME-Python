import torch
from ACME.utility.col  import *
from ACME.utility.find import *
from .ind2poly         import *
from .poly2edge        import *



def adjacency(E,W,size=None):
    """
    Computes the adjacency matrix with the given weights for the specified edges

    Parameters
    ----------
    E : LongTensor
        the (2,N,) edge topology tensor
    W : Tensor
        the (N,) edges weights tensor
    size : int (optional)
        the adjacency matrix size. If None it will be automatically computed (default is None)

    Returns
    -------
    Tensor
        the adjacency matrix
    """

    if size is None:
        size = E.max()+1
    A = torch.zeros(size,size,dtype=W.dtype,device=W.device)
    for i,j,w in zip(*tuple(torch.t(E)),W):
        A[i,j] += w
    return A



def edge2adj(E,size=None):
    """
    Computes the adjacency matrix from the given edge tensor

    Parameters
    ----------
    E : LongTensor
        the edge tensor
    size : int (optional)
        the adjacency matrix size. If None it will be automatically computed (default is None)

    Returns
    -------
    Tensor
        the adjacency matrix
    """

    return adjacency(E,torch.ones(col(E),dtype=torch.float,device=E.device),size=size)



def adj2edge(A):
    """
    Extracts the edges from an adjacency matrix.

    Parameters
    ----------
    A : Tensor
        the adjacency matrix

    Returns
    -------
    LongTensor
        the edge tensor
    """

    return torch.t(find(A>0,linear=False))



def poly2adj(T,size=None):
    """
    Computes the adjacency matrix for the given topology

    Parameters
    ----------
    T : LongTensor
        the topology tensor
    size : int (optional)
        the adjacency matrix size. If None it will be automatically computed (default is None)

    Returns
    -------
    Tensor
        the adjacency matrix
    """

    return edge2adj(poly2edge(T)[0],size=None)


