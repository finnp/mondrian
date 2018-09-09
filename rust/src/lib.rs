#[macro_use] extern crate cpython;

use cpython::{PyResult, Python};
use std::collections::HashSet;

type Line = (usize, usize, usize, usize);
type Lines = Vec<Line>;

// names: "myrustlib" must be the name of the `.so` or `.pyd` file
py_module_initializer!(myrustlib, initmyrustlib, PyInit_myrustlib, |py, m| {
    try!(m.add(py, "__doc__", "This module is implemented in Rust."));
    try!(m.add(py, "detect_lines", py_fn!(py, detect_lines(img: Vec<bool>, width: usize, height: usize, min_line_length: usize))));
    try!(m.add(py, "reduce_lines", py_fn!(py, reduce_lines(horizontal: Vec<Line>, vertical: Vec<Line>, min_distance: usize))));
    Ok(())
});

fn average(numbers: Vec<usize>) -> f64 {
    let mut total = 0;
    for index in 0..numbers.len() {
        total = total + numbers[index];
    }
    (total as f64) / (numbers.len() as f64)
}

fn reduce_lines(_: Python, horizontal: Vec<Line>, vertical: Vec<Line>, min_distance: usize) -> PyResult<(Lines, Lines)> {
    let mut seen_vertical = HashSet::new();
    let mut seen_horizontal = HashSet::new();
    let mut output_vertical = vec![];
    let mut output_horizontal = vec![];

    for index in 0..vertical.len() {
        if seen_vertical.contains(&index) {
            continue;
        }
        let (x1,mut y1,_x2,mut y2) = vertical[index];
        let mut x_values = vec![x1];
        for other_index in 0..vertical.len() {
            if seen_vertical.contains(&other_index) {
                continue;
            }
            let (x1_b,y1_b,_x2_b,y2_b) = vertical[other_index];
            if (x1 as isize - x1_b as isize).abs() < min_distance as isize {
                // if the end is further to the top, choose this end
                if y2_b < y2 {
                    y2 = y2_b;
                }
                // if the start if further to the bottom, choose it
                if y1_b > y1 {
                    y1 = y1_b;
                }

                x_values.push(x1_b);
                seen_vertical.insert(other_index);
            }
        }
        let x = average(x_values);
        output_vertical.push((x as usize,y1,x as usize,y2));
    }

    for index in 0..horizontal.len() {
        if seen_horizontal.contains(&index) {
            continue;
        }
        let (mut x1,y1,mut x2,_y2) = horizontal[index];
        let mut y_values = vec![y1];
        for other_index in 0..horizontal.len() {
            if seen_horizontal.contains(&other_index) {
                continue;
            }
            let (x1_b,y1_b,x2_b,_y2_b) = horizontal[other_index];
            if (y1 as isize - y1_b as isize).abs() < min_distance as isize {
                if x1_b < x1 {
                    x1 = x1_b;
                }
                if x2_b > x2 {
                    x2 = x2_b;
                }

                y_values.push(y1_b);
                seen_horizontal.insert(other_index);
            }
        }
        let y = average(y_values);
        output_horizontal.push((x1,y as usize,x2,y as usize))
    }

    return Ok((output_vertical, output_horizontal));

}

fn detect_lines(_: Python, img: Vec<bool>, width: usize, height: usize, min_line_length: usize) -> PyResult<Lines> {
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
