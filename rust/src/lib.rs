#[macro_use] extern crate cpython;

use cpython::{PyResult, Python};

// names: "myrustlib" must be the name of the `.so` or `.pyd` file
py_module_initializer!(myrustlib, initmyrustlib, PyInit_myrustlib, |py, m| {
    try!(m.add(py, "__doc__", "This module is implemented in Rust."));
    try!(m.add(py, "detect_lines", py_fn!(py, detect_lines(img: Vec<bool>, width: usize, height: usize, min_line_length: usize))));
    Ok(())
});

fn detect_lines(_: Python, img: Vec<bool>, width: usize, height: usize, min_line_length: usize) -> PyResult<Vec<(usize, usize, usize, usize)>> {
    let mut current_line = false;
    let mut current_line_start: usize = 0;
    let mut lines = vec![];

    // Horizontal
    for y in 0..height {
        for x in 0..width {
            let is_white = img[y * width + x];
            if is_white {
                if !current_line {
                    current_line = true;
                    current_line_start = x;
                }
            } else {
                if current_line {
                    current_line = false;
                    if x > 0 && x - current_line_start >= min_line_length {
                        lines.push((current_line_start, y, x - 1, y));
                    }
                }
            }
        }
        if current_line {
            current_line = false;
            if width - current_line_start >= min_line_length {
                lines.push((current_line_start, y, width - 1, y));
            }
        }
    }

    current_line = false;
    current_line_start = 0;

    // Vertical
    for x in 0..width {
        for y in 0..height {
            let is_white = img[y * width + x];
            if is_white {
                if !current_line {
                    current_line = true;
                    current_line_start = y;
                }
            } else {
                if current_line {
                    current_line = false;
                    if y > 0 && y - current_line_start >= min_line_length {
                        lines.push((x, y - 1,x, current_line_start));
                    }
                }
            }
        }
        if current_line {
            current_line = false;
            if height - current_line_start >= min_line_length {
                lines.push((x, height - 1,x, current_line_start));
            }
        }
    }

    Ok(lines)
}
