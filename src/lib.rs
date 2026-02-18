//Cspell:Ignore pymodule pyfunction
use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
mod stegano {
    use stegano_core::api::{Password, hide, unveil};
    
    use pyo3::exceptions::PyOSError;
    use pyo3::prelude::*;

    #[pyfunction]
    fn encode(password: &str, input_file: &str, output_file: &str, disguise_image: &str) -> PyResult<()> {
        match hide::prepare()
        // .with_message(message) //TODO - Doesn't show up when unveil, maybe an error on the main libs.
        .using_password(Password::from(password))
        .with_file(input_file)
        .with_output(output_file)
        .with_image(disguise_image)
        .execute() {
            Ok(_) => Ok(()),
            Err(err) => Err(PyOSError::new_err(err.to_string()))
        }
    }
        
    #[pyfunction]
    fn decode(password: &str, disguise_image: &str, output_folder: &str) -> PyResult<()> {
        match unveil::prepare()
        .using_password(Password::from(password))
        .from_secret_file(disguise_image)
        .into_output_folder(output_folder)
        .execute() {
            Ok(_) => Ok(()),
            Err(err) => Err(PyOSError::new_err(err.to_string()))
        }
    }
}