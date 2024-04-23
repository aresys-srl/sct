# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
Radar Cross Section computation utilities
-----------------------------------------
"""

import numpy as np
import numpy.typing as npt
from arepytools.geometry.conversions import xyz2llh


def compute_rcs_trihedral_corner_reflector(
    cr_arm_length_m: float, wavelength_m: float, elevation_rad: npt.ArrayLike, azimuth_rad: npt.ArrayLike
) -> npt.ArrayLike:
    """Computes the Radar Cross Section (RCS) of a trihedral corner reflector (CR) as observed by a radar source emitting
    at a certain wavelength.
    The function requires in input the size (arm length) of the CR, the frequency of the radar source, and the angular
    coordinates of the radar source as see by the corner reflector.

    The angular coordinates (elevation and azimuth) are expressed in a reference frame such that the three axes are
    parallel to the trihedral CR edges, with the xy plane parallel to the horizontal plate, so that:
    - the elevation is the angle between the viewing direction and the x-y plane, assumed to be parallel to the
    horizontal plate of the CR
    - the azimuth is the angle between the x-axis and the projection of the viewing direction on the x-y plane

    See Brock, Billy & Doerry, Armin. (2009). Radar cross section of triangular trihedral reflector with extended
    bottom plate. 10.2172/984946.

    Parameters
    ----------
    cr_arm_length_m : float
        Length of the arm of the trihedral corner reflector, expressed in m
    wavelength_m : float
        Wavelength of the radio wave impinging on the corner reflector, expressed in m
    elevation_rad : np.ndarray
        Elevation angle at which the corner reflector sees the source of radio waves, expressed in radians
    azimuth_rad : np.ndarray
        Azimuth angle at which the corner reflector sees the source of radio waves, expressed in radians

    Returns
    -------
    np.ndarray
        Radar Cross Section (RCS) of the trihedral corner reflector, expressed in meters squared

    """
    is_scalar = False if isinstance(elevation_rad, np.ndarray) else True
    elevation_rad = np.atleast_1d(elevation_rad)
    azimuth_rad = np.atleast_1d(azimuth_rad)

    is_elevation_range_valid = (elevation_rad >= 0) & (elevation_rad <= np.pi / 2)
    elevation_rad[~is_elevation_range_valid] = np.nan

    is_azimuth_range_valid = (azimuth_rad >= 0) & (azimuth_rad <= np.pi / 2)
    azimuth_rad[~is_azimuth_range_valid] = np.nan

    rcs_peak = 4 * np.pi * (cr_arm_length_m**4) / (wavelength_m**2)

    sin_elev = np.sin(elevation_rad)
    cos_elev_sin_azimuth = np.cos(elevation_rad) * np.sin(azimuth_rad)
    cos_elev_cos_azimuth = np.cos(elevation_rad) * np.cos(azimuth_rad)

    geometrical_condition = sin_elev + cos_elev_sin_azimuth <= cos_elev_cos_azimuth
    first_angular_dependency = (
        (4 * sin_elev * cos_elev_sin_azimuth) / (sin_elev + cos_elev_sin_azimuth + cos_elev_cos_azimuth)
    ) ** 2
    second_angular_dependency = (
        sin_elev
        + cos_elev_sin_azimuth
        + cos_elev_cos_azimuth
        - 2 / (sin_elev + cos_elev_sin_azimuth + cos_elev_cos_azimuth)
    ) ** 2
    angular_dependency = np.where(
        geometrical_condition,
        first_angular_dependency,
        second_angular_dependency,
    )

    result = rcs_peak * angular_dependency

    return result if not is_scalar else result[0]


def _compute_enu_axes(latitude_rad: float, longitude_rad: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Find the three vectors describing the axes of the ENU (East-North-Up)
    local reference frame for a point on Earth.
    Requires in input the angular coordinates of the point on Earth where to
    determine the ENU reference frame.

    See https://gssc.esa.int/navipedia/index.php/Transformations_between_ECEF_and_ENU_coordinates

    Parameters
    ----------
    latitude_rad : float
        Latitude of a ground point, in radians
    longitude_rad : float
        Longitude of a ground point, in radians

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        Tuple of three numpy arrays, each one is a 3D Cartesian vector of unit length specifying the axis of a
        orthogonal reference frame
    """

    cos_lat = np.cos(latitude_rad)
    sin_lat = np.sin(latitude_rad)
    cos_lon = np.cos(longitude_rad)
    sin_lon = np.sin(longitude_rad)

    east_unit_vector = np.array([-sin_lon, cos_lon, 0.0])
    north_unit_vector = np.array([-cos_lon * sin_lat, -sin_lon * sin_lat, cos_lat])
    up_unit_vector = np.array([cos_lon * cos_lat, sin_lon * cos_lat, sin_lat])

    return east_unit_vector, north_unit_vector, up_unit_vector


def compute_elevation_azimuth_wrt_enu(pos_cr: np.ndarray, pos_sat: np.ndarray) -> tuple[float, float]:
    """Computes the looking angles (elevation and azimuth) at which a point on ground (e.g. a corner reflector) sees
    another point in the sky (e.g. a satellite), with respect to its local ENU reference frame.

    Letting rho be the normalized line of sight vector pointing from the corner reflector to the satellite, and letting
    e, n, and u, the unit vectors of the ENU reference frame local to the corner reflector, then the elevation angle and
    azimuth angle are, respectively:

    .. math::
        E=\\arcsin(\\hat {\\boldsymbol \\rho}\\cdot \\hat{\\mathbf u})

        A=\\arctan \\left (\\frac{\\hat {\\boldsymbol \\rho}\\cdot \\hat{\\mathbf e}}{\\hat {\\boldsymbol \\rho}\\cdot \\hat{\\mathbf n}}\\right )

    N.B. elevation and azimuth here computed are expressed wrt local ENU reference frame, not wrt boresight

    See https://gssc.esa.int/navipedia/index.php/Transformations_between_ECEF_and_ENU_coordinates

    Parameters
    ----------
    pos_cr : np.ndarray
        (3, ) numpy array, expressing the 3D Cartesian position of a corner reflector on ground
    pos_sat : np.ndarray
        (3, ) numpy array, expressing the 3D Cartesian position of a satellite observing the corner reflector

    Returns
    -------
    tuple[float, float]
        Elevation and azimuth angles at which the corner reflector sees the satellite in its ENU local reference frame
    """

    lat_cr_rad, lon_cr_rad, _ = xyz2llh(pos_cr.flatten()).flatten()

    e, n, u = _compute_enu_axes(latitude_rad=lat_cr_rad, longitude_rad=lon_cr_rad)

    los = pos_sat - pos_cr
    los_normalized = los / np.linalg.norm(los)

    elevation_rad = np.arcsin(np.sum(los_normalized * u))
    azimuth_rad = np.arctan2(np.sum(los_normalized * e), np.sum(los_normalized * n))

    return elevation_rad, azimuth_rad
