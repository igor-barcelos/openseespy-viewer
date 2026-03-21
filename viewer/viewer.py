"""Main viewer logic: builds the 3D scene and runs the live preview loop."""

import os
import sys
import importlib
import numpy as np
import pyvista as pv

SCREENSHOT_DIR = os.path.join(os.getcwd(), 'images')
_screenshot_counter = 0

from .model import parse_py
from .watcher import start_watcher

# Default visual style
DEFAULTS = dict(
    bg_colour='lightgrey',
    node_colour='black',
    node_size=12,
    ele_colour='black',
    ele_width=2,
    axis_colour='grey',
    label_font_size=10,
    offset_ratio=0.02,
    bc_arrow_scale=0.3,
    min_refresh_interval=0.5,
    load_colour='red',
    load_arrow_scale=0.06,
)


def _nodecoords(nodetag, nodes, ndm):
    """Returns node coordinates as a 3D point (z=0 for 2D models)."""
    for node in nodes:
        if node[0] == nodetag:
            if ndm == 2:
                return np.array([node[1], node[2], 0.0])
            else:
                return np.array([node[1], node[2], node[3]])
    return None


def _build_scene(plotter, modelfiles, ndm, style):
    """Parse model files and add all geometry to the plotter."""
    nodes, elements, fixities, _, nodal_loads = parse_py(modelfiles)

    if not nodes:
        return

    # Build node points array (always 3D; z=0 for 2D models)
    if ndm == 2:
        node_points = np.array([[n[1], n[2], 0.0] for n in nodes])
    else:
        node_points = np.array([[n[1], n[2], n[3]] for n in nodes])

    node_tags = [n[0] for n in nodes]

    # Compute model size for offsets
    mins = node_points.min(axis=0)
    maxs = node_points.max(axis=0)
    spans = maxs - mins
    model_size = max(spans.max(), 1.0)
    offset = model_size * style['offset_ratio']

    # --- Display nodes ---
    node_cloud = pv.PolyData(node_points)
    plotter.add_mesh(node_cloud, color=style['node_colour'],
                     point_size=style['node_size'],
                     render_points_as_spheres=True)

    # Node labels
    label_points = node_points + offset
    node_labels = ['N' + str(t) for t in node_tags]
    plotter.add_point_labels(label_points, node_labels,
                             font_size=style['label_font_size'],
                             text_color='black', font_family='courier',
                             bold=True, shape=None, fill_shape=False)

    # --- Display reference axes ---
    if ndm == 2:
        margin = model_size * 0.15
        x_line = pv.Line([mins[0] - margin, 0, 0], [maxs[0] + margin, 0, 0])
        y_line = pv.Line([0, mins[1] - margin, 0], [0, maxs[1] + margin, 0])
        plotter.add_mesh(x_line, color=style['axis_colour'], line_width=1,
                         style='wireframe')
        plotter.add_mesh(y_line, color=style['axis_colour'], line_width=1,
                         style='wireframe')
    else:
        view_centre = (mins + maxs) / 2
        view_range = spans.max()
        axis_len = 1.2 * (view_range / 2 + max(abs(view_centre)))
        x_axis = pv.Line([0, 0, 0], [axis_len, 0, 0])
        y_axis = pv.Line([0, 0, 0], [0, axis_len, 0])
        z_axis = pv.Line([0, 0, 0], [0, 0, axis_len])
        plotter.add_mesh(x_axis, color='red', line_width=1)
        plotter.add_mesh(y_axis, color='green', line_width=1)
        plotter.add_mesh(z_axis, color='blue', line_width=1)

    # --- Display elements ---
    if elements:
        for element in elements:
            iNode = _nodecoords(element[2], nodes, ndm)
            jNode = _nodecoords(element[3], nodes, ndm)
            if iNode is not None and jNode is not None:
                line = pv.Line(iNode, jNode)
                plotter.add_mesh(line, color=style['ele_colour'],
                                 line_width=style['ele_width'])
                mid = (iNode + jNode) / 2 + offset
                plotter.add_point_labels(
                    [mid], ['E' + str(element[1])],
                    font_size=style['label_font_size'],
                    text_color='black', font_family='courier',
                    shape=None, fill_shape=False)

    # --- Display boundary conditions ---
    if fixities:
        bc_size = model_size * 0.04
        for fixity in fixities:
            coords = _nodecoords(fixity[0], nodes, ndm)
            if coords is None:
                continue

            if ndm == 2:
                if fixity[1] == 1:
                    tip = coords - np.array([bc_size * 0.5, 0, 0])
                    tri = pv.Triangle([
                        [tip[0] - bc_size, tip[1] - bc_size * 0.5, 0],
                        [tip[0], tip[1], 0],
                        [tip[0] - bc_size, tip[1] + bc_size * 0.5, 0],
                    ])
                    plotter.add_mesh(tri, color='black', style='wireframe',
                                     line_width=2)
                if fixity[2] == 1:
                    tip = coords - np.array([0, bc_size * 0.5, 0])
                    tri = pv.Triangle([
                        [tip[0] - bc_size * 0.5, tip[1] - bc_size, 0],
                        [tip[0], tip[1], 0],
                        [tip[0] + bc_size * 0.5, tip[1] - bc_size, 0],
                    ])
                    plotter.add_mesh(tri, color='black', style='wireframe',
                                     line_width=2)
                if len(fixity) > 3 and fixity[3] == 1:
                    circle = pv.Circle(radius=bc_size * 0.6, resolution=32)
                    circle.translate(coords, inplace=True)
                    plotter.add_mesh(circle, color='black', style='wireframe',
                                     line_width=2)
            else:
                directions = [
                    np.array([1, 0, 0]),
                    np.array([0, 1, 0]),
                    np.array([0, 0, 1]),
                ]
                for i, d in enumerate(directions):
                    if fixity[i + 1] == 1:
                        start = coords - d * bc_size * 1.5
                        arrow = pv.Arrow(start=start, direction=d,
                                         scale=bc_size * 1.5, tip_length=0.4,
                                         tip_radius=0.15, shaft_radius=0.05)
                        plotter.add_mesh(arrow, color='black')

    # --- Display nodal loads ---
    if nodal_loads:
        all_magnitudes = []
        for nl in nodal_loads:
            values = nl[1:]
            if ndm == 2:
                force_mag = np.linalg.norm(values[:2]) if len(values) >= 2 else 0
                moment_mag = abs(values[2]) if len(values) >= 3 else 0
            else:
                force_mag = np.linalg.norm(values[:3]) if len(values) >= 3 else 0
                moment_mag = np.linalg.norm(values[3:6]) if len(values) >= 6 else 0
            if force_mag > 0:
                all_magnitudes.append(force_mag)
            if moment_mag > 0:
                all_magnitudes.append(moment_mag)

        if all_magnitudes:
            max_mag = max(all_magnitudes)
            load_scale = (model_size * style['load_arrow_scale']) / max_mag
            arrow_size = model_size * style['load_arrow_scale']

            for nl in nodal_loads:
                tag = nl[0]
                values = nl[1:]
                coords = _nodecoords(tag, nodes, ndm)
                if coords is None:
                    continue

                # Force components
                if ndm == 2:
                    force = np.array([values[0] if len(values) > 0 else 0,
                                      values[1] if len(values) > 1 else 0,
                                      0.0])
                else:
                    force = np.array([values[0] if len(values) > 0 else 0,
                                      values[1] if len(values) > 1 else 0,
                                      values[2] if len(values) > 2 else 0])

                fmag = np.linalg.norm(force)
                if fmag > 1e-12:
                    fdir = force / fmag
                    length = fmag * load_scale
                    start = coords - fdir * length
                    arrow = pv.Arrow(start=start, direction=fdir,
                                     scale=length, tip_length=0.3,
                                     tip_radius=0.12, shaft_radius=0.04)
                    plotter.add_mesh(arrow, color=style['load_colour'])

                # Moment components
                if ndm == 2:
                    mz = values[2] if len(values) > 2 else 0
                    if abs(mz) > 1e-12:
                        arc_radius = arrow_size * 0.8
                        arc = pv.CircularArc(
                            [coords[0] + arc_radius, coords[1], coords[2]],
                            [coords[0], coords[1] + arc_radius, coords[2]],
                            coords, negative=(mz < 0), resolution=24)
                        plotter.add_mesh(arc, color=style['load_colour'],
                                         line_width=2)
                else:
                    moments = np.array([
                        values[3] if len(values) > 3 else 0,
                        values[4] if len(values) > 4 else 0,
                        values[5] if len(values) > 5 else 0])
                    arc_radius = arrow_size * 0.8
                    axes_info = [
                        (moments[0], [0, 1, 0], [0, 0, 1]),
                        (moments[1], [0, 0, 1], [1, 0, 0]),
                        (moments[2], [1, 0, 0], [0, 1, 0]),
                    ]
                    for mval, dir1, dir2 in axes_info:
                        if abs(mval) > 1e-12:
                            p1 = coords + np.array(dir1) * arc_radius
                            p2 = coords + np.array(dir2) * arc_radius
                            arc = pv.CircularArc(p1, p2, coords,
                                                 negative=(mval < 0),
                                                 resolution=24)
                            plotter.add_mesh(arc, color=style['load_colour'],
                                             line_width=2)


def view(*modelfiles, **kwargs):
    """Open a live viewer for the given OpenSeesPy model file(s).

    Parameters
    ----------
    *modelfiles : str
        One or more paths to OpenSeesPy model files (.py).
    **kwargs :
        Optional style overrides (bg_colour, node_colour, node_size,
        ele_colour, ele_width, axis_colour, label_font_size, offset_ratio,
        min_refresh_interval).
    """
    if not modelfiles:
        raise ValueError("At least one model file path is required.")

    style = {**DEFAULTS, **kwargs}

    # Determine 2D or 3D
    _, _, _, ndm, _ = parse_py(modelfiles)

    # Start file watcher
    observer, file_handler, lib_handler = start_watcher(modelfiles)

    # Create plotter
    plotter = pv.Plotter(title='OpenSeesPy Viewer - ' + ', '.join(modelfiles))
    plotter.set_background(style['bg_colour'])

    # Initial scene build
    _build_scene(plotter, modelfiles, ndm, style)

    if ndm == 2:
        plotter.view_xy()
        plotter.enable_parallel_projection()

    def _update(step):
        need_redraw = file_handler.changed.is_set()

        if lib_handler.changed.is_set():
            lib_handler.changed.clear()
            try:
                from viewer import model as _model_mod
                importlib.reload(_model_mod)
                importlib.reload(sys.modules[__name__])
                style.update({**sys.modules[__name__].DEFAULTS, **kwargs})
                print("[HMR] Viewer reloaded.")
            except Exception as e:
                print(f"[HMR] Reload failed: {e}")
            need_redraw = True

        if not need_redraw:
            return

        file_handler.changed.clear()
        plotter.clear()
        sys.modules[__name__]._build_scene(plotter, modelfiles, ndm, style)
        if ndm == 2:
            plotter.view_xy()
        plotter.render()

    def _screenshot():
        global _screenshot_counter
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        _screenshot_counter += 1
        path = os.path.join(SCREENSHOT_DIR, f'model_screenshot_{_screenshot_counter:03d}.png')
        plotter.screenshot(path)
        print(f'Screenshot saved to {path}')

    plotter.add_key_event('s', _screenshot)

    plotter.show(interactive_update=True)
    plotter.add_timer_event(
        max_steps=sys.maxsize,
        duration=int(style['min_refresh_interval'] * 1000),
        callback=_update,
    )

    try:
        plotter.iren.start()
    finally:
        observer.stop()
        observer.join()
