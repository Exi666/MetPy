#  Copyright (c) 2019 MetPy Developers.
#  Distributed under the terms of the BSD 3-Clause License.
#  SPDX-License-Identifier: BSD-3-Clause
"""Test the simplified plotting interface."""

from datetime import datetime
from io import BytesIO
import warnings

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib
import pytest
from traitlets import TraitError
import xarray as xr

from metpy.cbook import get_test_data
from metpy.io import GiniFile
from metpy.plots import (BarbPlot, ContourPlot, FilledContourPlot, ImagePlot, MapPanel,
                         PanelContainer)
# Fixtures to make sure we have the right backend
from metpy.testing import set_agg_backend  # noqa: F401, I202
from metpy.units import units


MPL_VERSION = matplotlib.__version__[:3]


@pytest.mark.mpl_image_compare(remove_text=True,
                               tolerance={'2.0': 3.09}.get(MPL_VERSION, 0.005))
def test_declarative_image():
    """Test making an image plot."""
    data = xr.open_dataset(GiniFile(get_test_data('NHEM-MULTICOMP_1km_IR_20151208_2100.gini')))

    img = ImagePlot()
    img.data = data.metpy.parse_cf('IR')
    img.colormap = 'Greys_r'

    panel = MapPanel()
    panel.title = 'Test'
    panel.plots = [img]

    pc = PanelContainer()
    pc.panel = panel
    pc.draw()

    assert panel.ax.get_title() == 'Test'

    return pc.figure


@pytest.mark.mpl_image_compare(remove_text=True, tolerance=0.022)
def test_declarative_contour():
    """Test making a contour plot."""
    data = xr.open_dataset(get_test_data('narr_example.nc', as_file_obj=False))

    contour = ContourPlot()
    contour.data = data
    contour.field = 'Temperature'
    contour.level = 700 * units.hPa
    contour.contours = 30
    contour.linewidth = 1
    contour.linecolor = 'red'

    panel = MapPanel()
    panel.area = 'us'
    panel.proj = 'lcc'
    panel.layers = ['coastline', 'borders', 'usstates']
    panel.plots = [contour]

    pc = PanelContainer()
    pc.size = (8, 8)
    pc.panels = [panel]
    pc.draw()

    return pc.figure


@pytest.mark.mpl_image_compare(remove_text=True, tolerance=0.035)
def test_declarative_contour_options():
    """Test making a contour plot."""
    data = xr.open_dataset(get_test_data('narr_example.nc', as_file_obj=False))

    contour = ContourPlot()
    contour.data = data
    contour.field = 'Temperature'
    contour.level = 700 * units.hPa
    contour.contours = 30
    contour.linewidth = 1
    contour.linecolor = 'red'
    contour.linestyle = 'dashed'
    contour.clabels = True

    panel = MapPanel()
    panel.area = 'us'
    panel.proj = 'lcc'
    panel.layers = ['coastline', 'borders', 'usstates']
    panel.plots = [contour]

    pc = PanelContainer()
    pc.size = (8, 8)
    pc.panels = [panel]
    pc.draw()

    return pc.figure


@pytest.mark.mpl_image_compare(remove_text=True, tolerance=0.016)
def test_declarative_events():
    """Test that resetting traitlets properly propagates."""
    data = xr.open_dataset(get_test_data('narr_example.nc', as_file_obj=False))

    contour = ContourPlot()
    contour.data = data
    contour.field = 'Temperature'
    contour.level = 850 * units.hPa
    contour.contours = 30
    contour.linewidth = 1
    contour.linecolor = 'red'

    img = ImagePlot()
    img.data = data
    img.field = 'v_wind'
    img.level = 700 * units.hPa
    img.colormap = 'hot'
    img.image_range = (3000, 5000)

    panel = MapPanel()
    panel.area = 'us'
    panel.proj = 'lcc'
    panel.layers = ['coastline', 'borders', 'states']
    panel.plots = [contour, img]

    pc = PanelContainer()
    pc.size = (8, 8)
    pc.panels = [panel]
    pc.draw()

    # Update some properties to make sure it regenerates the figure
    contour.linewidth = 2
    contour.linecolor = 'green'
    contour.level = 700 * units.hPa
    contour.field = 'Specific_humidity'
    img.field = 'Geopotential_height'
    img.colormap = 'plasma'
    img.colorbar = 'horizontal'

    return pc.figure


def test_no_field_error():
    """Make sure we get a useful error when the field is not set."""
    data = xr.open_dataset(get_test_data('narr_example.nc', as_file_obj=False))

    contour = ContourPlot()
    contour.data = data
    contour.level = 700 * units.hPa

    with pytest.raises(ValueError):
        contour.draw()


def test_no_field_error_barbs():
    """Make sure we get a useful error when the field is not set."""
    data = xr.open_dataset(get_test_data('narr_example.nc', as_file_obj=False))

    barbs = BarbPlot()
    barbs.data = data
    barbs.level = 700 * units.hPa

    with pytest.raises(TraitError):
        barbs.draw()


def test_projection_object():
    """Test that we can pass a custom map projection."""
    data = xr.open_dataset(get_test_data('narr_example.nc', as_file_obj=False))

    contour = ContourPlot()
    contour.data = data
    contour.level = 700 * units.hPa
    contour.field = 'Temperature'

    panel = MapPanel()
    panel.area = (-110, -60, 25, 55)
    panel.projection = ccrs.Mercator()
    panel.layers = [cfeature.LAKES]
    panel.plots = [contour]

    pc = PanelContainer()
    pc.panel = panel
    pc.draw()

    return pc.figure


@pytest.mark.mpl_image_compare(remove_text=True, tolerance=0.016)
def test_colorfill():
    """Test that we can use ContourFillPlot."""
    data = xr.open_dataset(get_test_data('narr_example.nc', as_file_obj=False))

    contour = FilledContourPlot()
    contour.data = data
    contour.level = 700 * units.hPa
    contour.field = 'Temperature'
    contour.colormap = 'coolwarm'
    contour.colorbar = 'vertical'

    panel = MapPanel()
    panel.area = (-110, -60, 25, 55)
    panel.layers = [cfeature.STATES]
    panel.plots = [contour]

    pc = PanelContainer()
    pc.panel = panel
    pc.size = (12, 8)
    pc.draw()

    return pc.figure


@pytest.mark.mpl_image_compare(remove_text=True, tolerance=0.016)
def test_colorfill_horiz_colorbar():
    """Test that we can use ContourFillPlot."""
    data = xr.open_dataset(get_test_data('narr_example.nc', as_file_obj=False))

    contour = FilledContourPlot()
    contour.data = data
    contour.level = 700 * units.hPa
    contour.field = 'Temperature'
    contour.colormap = 'coolwarm'
    contour.colorbar = 'horizontal'

    panel = MapPanel()
    panel.area = (-110, -60, 25, 55)
    panel.layers = [cfeature.STATES]
    panel.plots = [contour]

    pc = PanelContainer()
    pc.panel = panel
    pc.size = (8, 8)
    pc.draw()

    return pc.figure


@pytest.mark.mpl_image_compare(remove_text=True, tolerance=0.016)
def test_colorfill_no_colorbar():
    """Test that we can use ContourFillPlot."""
    data = xr.open_dataset(get_test_data('narr_example.nc', as_file_obj=False))

    contour = FilledContourPlot()
    contour.data = data
    contour.level = 700 * units.hPa
    contour.field = 'Temperature'
    contour.colormap = 'coolwarm'
    contour.colorbar = None

    panel = MapPanel()
    panel.area = (-110, -60, 25, 55)
    panel.layers = [cfeature.STATES]
    panel.plots = [contour]

    pc = PanelContainer()
    pc.panel = panel
    pc.size = (8, 8)
    pc.draw()

    return pc.figure


@pytest.mark.mpl_image_compare(remove_text=True, tolerance=1.23)
def test_global():
    """Test that we can set global extent."""
    data = xr.open_dataset(GiniFile(get_test_data('NHEM-MULTICOMP_1km_IR_20151208_2100.gini')))

    img = ImagePlot()
    img.data = data
    img.field = 'IR'
    img.colorbar = None

    panel = MapPanel()
    panel.area = 'global'
    panel.plots = [img]

    pc = PanelContainer()
    pc.panel = panel
    pc.draw()

    return pc.figure


@pytest.mark.mpl_image_compare(remove_text=True)
@pytest.mark.xfail(xr.__version__ < '0.11.0', reason='Does not work with older xarray.')
def test_latlon():
    """Test our handling of lat/lon information."""
    data = xr.open_dataset(get_test_data('irma_gfs_example.nc', as_file_obj=False))

    img = ImagePlot()
    img.data = data
    img.field = 'Temperature_isobaric'
    img.level = 500 * units.hPa
    img.time = datetime(2017, 9, 5, 15, 0, 0)
    img.colorbar = None

    contour = ContourPlot()
    contour.data = data
    contour.field = 'Geopotential_height_isobaric'
    contour.level = img.level
    contour.time = img.time

    panel = MapPanel()
    panel.projection = 'lcc'
    panel.area = 'us'
    panel.plots = [img, contour]

    pc = PanelContainer()
    pc.panel = panel
    pc.draw()

    return pc.figure


@pytest.mark.mpl_image_compare(remove_text=True, tolerance=0.37)
def test_declarative_barb_options():
    """Test making a contour plot."""
    data = xr.open_dataset(get_test_data('narr_example.nc', as_file_obj=False))

    barb = BarbPlot()
    barb.data = data
    barb.level = 300 * units.hPa
    barb.field = ['u_wind', 'v_wind']
    barb.skip = (10, 10)
    barb.color = 'blue'
    barb.pivot = 'tip'
    barb.barblength = 6.5

    panel = MapPanel()
    panel.area = 'us'
    panel.projection = 'data'
    panel.layers = ['coastline', 'borders', 'usstates']
    panel.plots = [barb]

    pc = PanelContainer()
    pc.size = (8, 8)
    pc.panels = [panel]
    pc.draw()

    return pc.figure


@pytest.mark.mpl_image_compare(remove_text=True, tolerance=0.612)
def test_declarative_barb_earth_relative():
    """Test making a contour plot."""
    import numpy as np
    data = xr.open_dataset(get_test_data('NAM_test.nc', as_file_obj=False))

    contour = ContourPlot()
    contour.data = data
    contour.field = 'Geopotential_height_isobaric'
    contour.level = 300 * units.hPa
    contour.linecolor = 'red'
    contour.linestyle = '-'
    contour.linewidth = 2
    contour.contours = np.arange(0, 20000, 120).tolist()

    barb = BarbPlot()
    barb.data = data
    barb.level = 300 * units.hPa
    barb.time = datetime(2016, 10, 31, 12)
    barb.field = ['u-component_of_wind_isobaric', 'v-component_of_wind_isobaric']
    barb.skip = (5, 5)
    barb.color = 'black'
    barb.barblength = 6.5
    barb.earth_relative = False

    panel = MapPanel()
    panel.area = (-124, -72, 20, 53)
    panel.projection = 'lcc'
    panel.layers = ['coastline', 'borders', 'usstates']
    panel.plots = [contour, barb]

    pc = PanelContainer()
    pc.size = (8, 8)
    pc.panels = [panel]
    pc.draw()

    return pc.figure


@pytest.mark.mpl_image_compare(remove_text=True, tolerance=0.346)
def test_declarative_barb_gfs():
    """Test making a contour plot."""
    data = xr.open_dataset(get_test_data('GFS_test.nc', as_file_obj=False))

    barb = BarbPlot()
    barb.data = data
    barb.level = 300 * units.hPa
    barb.field = ['u-component_of_wind_isobaric', 'v-component_of_wind_isobaric']
    barb.skip = (2, 2)
    barb.earth_relative = False

    panel = MapPanel()
    panel.area = 'us'
    panel.projection = 'data'
    panel.layers = ['coastline', 'borders', 'usstates']
    panel.plots = [barb]

    pc = PanelContainer()
    pc.size = (8, 8)
    pc.panels = [panel]
    pc.draw()

    barb.level = 700 * units.hPa

    return pc.figure


def test_save():
    """Test that our saving function works."""
    pc = PanelContainer()
    fobj = BytesIO()
    pc.save(fobj, format='png')

    fobj.seek(0)

    # Test that our file object had something written to it.
    assert fobj.read()


def test_show():
    """Test that show works properly."""
    pc = PanelContainer()

    # Matplotlib warns when using show with Agg
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)
        pc.show()


def test_panel():
    """Test the functionality of the panel property."""
    panel = MapPanel()

    pc = PanelContainer()
    pc.panels = [panel]

    assert pc.panel is panel

    pc.panel = panel
    assert pc.panel is panel
