import torch
from ..math.tan                     import *
from ..math.cart2homo               import *
from ..math.cart2sph                import *
from ..math.deg2rad                 import *
from ..math.homo2cart               import *
from ..math.sph2cart                import *
from ..math.sph2rotm                import *
from ..topology.ind2poly            import *
from ..topology.poly2edge           import *
from ..topology.poly2unique         import *
from ..geometry.equilateral_polygon import *
from ..geometry.octahedron          import *
from ..geometry.icosahedron         import *
from ..geometry.sphere              import *
from ..geometry.soup2mesh           import *


class CameraExtrinsic(object):
    """
    A class representing the camera extrinsic properties

    Attributes
    ----------
    position : Tensor
        the camera position
    target : Tensor
        the camera target
    up_vector : Tensor
        the camera up vector
    device : str or torch.device
        the device to store the tensors to

    Methods
    -------
    look_at(target)
        sets the camera target
    look_from(position)
        sets the camera position
    direction()
        returns the camera direction
    view_matrix()
        returns the current view matrix
    to(**kwargs)
        changes extrinsic dtype and/or device
    """

    def __init__(self, position=(0, 0, 0), target=(0, 0, 1), up_vector=(0, 1, 0), device='cuda:0'):
        """
        Parameters
        ----------
        position : list or tuple (optional)
            the camera position (default is (0, 0, 0))
        target : list or tuple (optional)
            the camera target (default is (0, 0, 1))
        up_vector : list or tuple (optional)
            the camera up vector (default is (0, 1, 0))
        device : str or torch.device (optional)
            the device to store the tensors to (default is 'cuda:0')
        """

        self.position  = torch.tensor(position,  dtype=torch.float, device=device)
        self.target    = torch.tensor(target,    dtype=torch.float, device=device)
        self.up_vector = torch.tensor(up_vector, dtype=torch.float, device=device)
        self.device    = device

    def look_at(self, target):
        """
        Sets the camera target

        Parameters
        ----------
        target : Tensor
            the (3,) target tensor

        Returns
        -------
        CameraExtrinsic
            the extrinsic itself
        """

        self.target = target
        return self

    def look_from(self, position):
        """
        Sets the camera position

        Parameters
        ----------
        position : Tensor
            the (3,) position tensor

        Returns
        -------
        CameraExtrinsic
            the extrinsic itself
        """

        self.position = position
        return self

    def direction(self):
        """
        Returns the camera direction

        Returns
        -------
        Tensor
            the (3,) direction tensor
        """

        return self.target - self.position

    def view_matrix(self):
        """
        Returns the current view matrix

        Returns
        -------
        Tensor
            a (4,4,) view matrix
        """

        z = normr(self.direction().unsqueeze(0))
        x = normr(cross(self.up_vector.unsqueeze(0), z))
        y = cross(z, x)
        p = self.position.unsqueeze(0)
        M = torch.cat((torch.cat((x.t(), y.t(), z.t(), -p.t()), dim=1),
                       torch.tensor([[0, 0, 0, 1]], dtype=torch.float, device=self.device)),
                      dim=0)
        return M

    def to(self, **kwargs):
        """
        Changes the extrinsic dtype and/or device

        Parameters
        ----------
        kwargs : ...

        Returns
        -------
        CameraExtrinsic
            the extrinsic itself
        """

        if 'device' in kwargs:
            self.device = kwargs['device']
        self.position  = self.position.to(**kwargs)
        self.target    = self.target.to(**kwargs)
        self.up_vector = self.up_vector.to(**kwargs)
        return self

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if key == 'device':
            self.position = self.position.to(self.device)
            self.target = self.target.to(self.device)
            self.up_vector = self.up_vector.to(self.device)


class CameraIntrinsic(object):
    """
    A class representing the camera intrinsic

    Attributes
    ----------
    fov : float
        the camera field of view angle in degrees
    near : float
        the near clipping plane distance
    far : float
        the far clipping plane distance
    image_size : tuple or list
        the image width and height
    projection : str
        the camera projection type ('orthographic' or 'perspective')
    device : str or torch.device
        the device to store the tensors to

    Methods
    -------
    aspect()
        returns the aspect ratio of the image
    projection_matrix()
        returns the current projection matrix
    orthographic_matrix()
        returns the current orthographic matrix
    perspective_matrix()
        returns the current perspective matrix
    to(**kwargs)
        changes the intrinsic device
    """

    def __init__(self, fov=30, near=0.1, far=10, image_size=(256, 256), projection='perspective', device='cuda:0'):
        """
        Parameters
        ----------
        fov : float (optional)
            the camera field of view in degrees (default is 30)
        near : float (optional)
            the camera near clipping plane distance (default is 0.1)
        far : float (optional)
            the camera far clipping plane distance (default is 10)
        image_size : list or tuple (optional)
            the image width and height (default is (256, 256))
        projection : str (optional)
            the projection type (default is 'perspective')
        device : str or torch.device (optional)
            the device to store the tensors to (default is 'cuda:0')
        """

        self.fov        = fov
        self.near       = near
        self.far        = far
        self.image_size = image_size
        self.projection = projection
        self.device     = device

    def aspect(self):
        """
        Returns the aspect ratio of the image

        Returns
        -------
        float
            the aspect ratio
        """
        return self.image_size[0] / self.image_size[1]

    def projection_matrix(self):
        """
        Returns the current projection matrix

        Returns
        -------
        Tensor
            a (4,4,) projection matrix
        """

        if self.projection == 'orthographic':
            return self.orthographic_matrix()
        if self.projection == 'perspective':
            return self.perspective_matrix()
        raise ValueError('Unknown projection type.')

    def orthographic_matrix(self):
        """
        Returns the orthographic projection matrix

        Returns
        -------
        Tensor
            a (4,4,) projection matrix
        """

        fov = deg2rad(self.fov)
        M = torch.zeros(4, 4, device=self.device)
        M[0, 0] = 1 / (self.aspect() * tan(fov / 2))
        M[1, 1] = 1 / tan(fov / 2)
        M[2, 2] = 2 / (self.far - self.near)
        M[2, 3] = -(self.far + self.near) / (self.far - self.near)
        M[3, 3] = 1
        return M

    def perspective_matrix(self):
        """
        Returns the perspective projection matrix

        Returns
        -------
        Tensor
            a (4,4,) projection matrix
        """

        fov = deg2rad(self.fov)
        M = torch.zeros(4, 4, device=self.device)
        M[0, 0] = 1 / (self.aspect() * tan(fov / 2))
        M[1, 1] = 1 / tan(fov / 2)
        M[2, 2] = (self.far + self.near) / (self.far - self.near)
        M[2, 3] = -2 * (self.far * self.near) / (self.far - self.near)
        M[3, 2] = 1
        return M

    def to(self, **kwargs):
        """
        Changes the the intrinsic device

        Parameters
        ----------
        kwargs : ...

        Returns
        -------
        CameraIntrinsic
            the intrinsic itself
        """

        if 'device' in kwargs:
            self.device = kwargs['device']
        return self


class Camera(object):
    """
    A class representing a camera

    Attributes
    ----------
    extrinsic : CameraExtrinsic
        the camera extrinsic
    intrinsic : CameraIntrinsic
        the camera intrinsic
    name : str
        the camera name
    device : str or torch.device
        the device to store the tensors to

    Methods
    -------
    project(P)
        projects the given 3D points into the 2D image
    unproject(Q)
        unprojects the given 2D points + depth to 3D space
    to(**kwargs)
        changes the camera dtype and/or device
    """

    def __init__(self,
                 extrinsic=CameraExtrinsic(),
                 intrinsic=CameraIntrinsic(),
                 name='Camera', device='cuda:0'):
        """
        Parameters
        ----------
        extrinsic : CameraExtrinsic (optional)
            the camera extrinsic (default is CameraExtrinsic())
        intrinsic : CameraIntrinsic (optional)
            the camera intrinsic (default is CameraIntrinsic())
        name : str (optional)
            the name of the camera (default is 'Camera')
        device : str or torch.device (optional)
            the device to store the tensors to
        """

        self.extrinsic = extrinsic
        self.intrinsic = intrinsic
        self.name      = name
        self.device    = device

    def project(self, P, pixels=True, dim=-1):
        """
        Projects the given 3D points into the 2D image

        Parameters
        ----------
        P : Tensor
            a (N,3,) points set tensor
        pixels : bool (optional)
            if True the UVs are returned in floating point pixel coordinates

        Returns
        -------
        Tensor
            a (N,3,) tensor containing UVs and depth
        """

        s = 0.5
        if pixels:
            # Image width and height
            w = self.intrinsic.image_size[0] - 1
            h = self.intrinsic.image_size[1] - 1
            t = torch.ones(P.ndimension(), dtype=torch.long, device=P.device)
            t[dim] = -1
            # Normalization factor (bring the coordinates from [-1,1] to [0, w], [0, h] and [0, 1] respectively)
            s *= torch.tensor([w, h, 1], dtype=torch.float, device=self.device).view(*t)
        # Transform the points into homogeneous coordinates, transform them into camera space and then project them
        UVd = torch.matmul(cart2homo(P, w=1, dim=dim),
                           torch.transpose(torch.matmul(self.intrinsic.projection_matrix(),
                                                        self.extrinsic.view_matrix()),
                                           -1, -2)
                           )
        # Bring the points into normalized homogeneous coordinates and normalize their values
        return homo2cart(UVd, dim=dim) * s + s

    def unproject(self, UVd, pixels=True, dim=-1):
        """
        Unprojects the given 2D points + depth to 3D space

        Parameters
        ----------
        UVd : Tensor
            a (N,3,) points set tensor consisting of UVs and depth values
        pixels : bool (optional)
            if True, the UVs are treated as floating point pixel coordinates

        Returns
        -------
        Tensor
            a (N,3,) points set tensor
        """

        s = 2
        if pixels:
            # Image width and height
            w = self.intrinsic.image_size[0] - 1
            h = self.intrinsic.image_size[1] - 1
            t = torch.ones(UVd.ndimension(), dtype=torch.long, device=P.device)
            t[dim] = -1
            # Normalization factor (brings the coordinates to [-1, 1])
            s /= torch.tensor([w, h, 1], dtype=torch.float, device=self.device).view(*t)
        # Change the points domain, transform them into homogeneous, and invert the projection process
        P = torch.matmul(cart2homo(UVd * s - 1, w=1, dim=dim),
                         torch.inverse(torch.matmul(self.intrinsic.projection_matrix(),
                                                    self.extrinsic.view_matrix())).t())
        # Normalize the coordinates
        return homo2cart(P, dim=dim)

    def to(self, **kwargs):
        """
        Changes the camera dtype and/or device

        Parameters
        ----------
        kwargs : ...

        Returns
        -------
        Camera
            the camera itself
        """

        if 'device' in kwargs:
            self.device = kwargs['device']
        self.extrinsic.to(**kwargs)
        self.intrinsic.to(**kwargs)
        return self

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if key == 'device':
            self.extrinsic.to(device=self.device)
            self.intrinsic.to(device=self.device)


def bokeh_camera(P, n=4, aperture=PI_16):
    """
    Creates a set of n positions around the given one

    Parameters
    ----------
    P : Tensor
        a (1,3,) tensor
    n : int (optional)
        the number of positions to generate (default is 4)
    aperture : float (optional)
        the aperture angle in radians (default is PI/16)

    Returns
    -------
    Tensor
        a (N+1,3,) tensor
    """

    Q = torch.cat((torch.zeros_like(P), aperture*equilateral_polygon(n, device=P.device)), dim=0)
    return sph2cart(cart2sph(P)+Q[:, (2, 0, 1)])


def camera_stage(tile=(6, 4), camera_distance=1, to_spherical=False, device='cuda:0'):
    """
    Returns the positions of a camera lying on the vertices of a sphere with given tiling

    Parameters
    ----------
    tile : tuple (optional)
        the sphere elevation-azimuth tiling (default is (6,4))
    camera_distance : float (optional)
        the camera distance from the origin (default is 1)
    to_spherical : bool (optional)
        if True, converts the coordinates into spherical (default is False)
    device : str or torch.device
        the device the tensors will be stored to (default is 'cuda:0')

    Returns
    -------
    (Tensor,LongTensor)
        the positions and the edge tensor of the camera views
    """

    P, T  = Sphere(tile=tile, device=device)[0:2]
    P,T   = soup2mesh(P, T)[0:2]
    theta = PI/100
    R     = torch.tensor([[1, 0, 0],
                          [0, cos(theta), -sin(theta)],
                          [0, sin(theta), cos(theta)]], dtype=torch.float, device=device)
    P     = torch.mul(torch.mm(P, torch.t(R)), camera_distance)
    E = torch.cat((poly2edge(T)[0],
                   poly2edge(torch.cat((ind2edge(T[0], T[2]),
                                        ind2edge(T[1], T[3])), dim=1))[0]),
                  dim=1)
    E = poly2unique(E[:, E[0] != E[1]], winding=True)[0]
    if to_spherical:
        P = cart2sph(P)
    return P, E


def camera_from_polyhedron(polyhedronFcn, camera_distance=1, to_spherical=False, device='cuda:0'):
    """
    Returns the positions of a camera lying on the vertices of a given polyhedron

    Parameters
    ----------
    polyhedronFcn : callable
        the polyhedron creation function
    camera_distance : float (optional)
        the camera distance from the origin (default is 1)
    to_spherical : bool (optional)
        if True, converts the coordinates into spherical (default is False)
    device : str or torch.device
        the device the tensors will be stored to (default is 'cuda:0')

    Returns
    -------
    (Tensor,LongTensor)
        the positions and the edge tensor of the camera views
    """

    P, T  = polyhedronFcn(device=device)[0:2]
    theta = PI/100
    R     = torch.tensor([[1, 0, 0],
                          [0, cos(theta), -sin(theta)],
                          [0, sin(theta), cos(theta)]], dtype=torch.float, device=device)
    P     = torch.mul(torch.mm(normr(P), torch.t(R)), camera_distance)
    if to_spherical:
        P = cart2sph(P)
    return P, poly2edge(T)[0]


def camera_6(camera_distance=1, to_spherical=False, device='cuda:0'):
    """
    Returns the positions of a camera lying on the vertices of an octahedron

    Parameters
    ----------
    camera_distance : float (optional)
        the camera distance from the origin (default is 1)
    to_spherical : bool (optional)
        if True, converts the coordinates into spherical (default is False)
    device : str or torch.device
        the device the tensors will be stored to (default is 'cuda:0')

    Returns
    -------
    (Tensor,LongTensor)
        the positions and the edge tensor of the camera views
    """

    return camera_from_polyhedron(Octahedron, camera_distance=camera_distance, to_spherical=to_spherical, device=device)


def camera_12(camera_distance=1, to_spherical=False, device='cuda:0'):
    """
    Returns the positions of a camera lying on the vertices of an icosahedron

    Parameters
    ----------
    camera_distance : float (optional)
        the camera distance from the origin (default is 1)
    to_spherical : bool (optional)
        if True, converts the coordinates into spherical (default is False)
    device : str or torch.device
        the device the tensors will be stored to (default is 'cuda:0')

    Returns
    -------
    (Tensor,LongTensor)
        the positions and the edge tensor of the camera views
    """

    return camera_from_polyhedron(Icosahedron, camera_distance=camera_distance, to_spherical=to_spherical, device=device)


def camera_18(camera_distance=1, to_spherical=False, device='cuda:0'):
    """
    Returns the positions of a camera lying on the vertices of a subdivided octahedron

    Parameters
    ----------
    camera_distance : float (optional)
        the camera distance from the origin (default is 1)
    to_spherical : bool (optional)
        if True, converts the coordinates into spherical (default is False)
    device : str or torch.device
        the device the tensors will be stored to (default is 'cuda:0')

    Returns
    -------
    (Tensor,LongTensor)
        the positions and the edge tensor of the camera views
    """

    return camera_from_polyhedron(Octahedron_2, camera_distance=camera_distance, to_spherical=to_spherical, device=device)


def camera_42(camera_distance=1, to_spherical=False, device='cuda:0'):
    """
    Returns the positions of a camera lying on the vertices of a subdivided icosahedron

    Parameters
    ----------
    camera_distance : float (optional)
        the camera distance from the origin (default is 1)
    to_spherical : bool (optional)
        if True, converts the coordinates into spherical (default is False)
    device : str or torch.device
        the device the tensors will be stored to (default is 'cuda:0')

    Returns
    -------
    (Tensor,LongTensor)
        the positions and the edge tensor of the camera views
    """

    return camera_from_polyhedron(Icosahedron_2, camera_distance=camera_distance, to_spherical=to_spherical, device=device)


def camera_66(camera_distance=1, to_spherical=False, device='cuda:0'):
    """
    Returns the positions of a camera lying on the vertices of a twice subdivided octahedron

    Parameters
    ----------
    camera_distance : float (optional)
        the camera distance from the origin (default is 1)
    to_spherical : bool (optional)
        if True, converts the coordinates into spherical (default is False)
    device : str or torch.device
        the device the tensors will be stored to (default is 'cuda:0')

    Returns
    -------
    (Tensor,LongTensor)
        the positions and the edge tensor of the camera views
    """

    return camera_from_polyhedron(Octahedron_3, camera_distance=camera_distance, to_spherical=to_spherical, device=device)


def camera_n(n, camera_distance=1, to_spherical=False, device='cuda:0'):
    """
    Returns the positions of a camera lying on the vertices of a equilateral polygon on the XY plane

    Parameters
    ----------
    n : float
        the number of vertices in the polygon
    camera_distance : float (optional)
        the camera distance from the origin (default is 1)
    to_spherical : bool (optional)
        if True, converts the coordinates into spherical (default is False)
    device : str or torch.device
        the device the tensors will be stored to (default is 'cuda:0')

    Returns
    -------
    (Tensor,LongTensor)
        the positions and the topology of the camera views
    """

    P = torch.mul(equilateral_polygon(n, device=device), camera_distance)
    E = torch.t(torch.cat((indices(0, n-2, device=device), indices(1, n-1, device=device)), dim=1))
    if to_spherical:
        P = cart2sph(P)
    return P, poly2edge(E)[0]
