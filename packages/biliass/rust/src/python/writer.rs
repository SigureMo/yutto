use crate::writer;

use pyo3::prelude::*;

#[pyfunction(name = "convert_timestamp")]
pub fn py_convert_timestamp(timestamp: f64) -> PyResult<String> {
    Ok(writer::utils::convert_timestamp(timestamp))
}

#[pyfunction(name = "ass_escape")]
pub fn py_ass_escape(text: &str) -> PyResult<String> {
    Ok(writer::utils::ass_escape(text))
}
