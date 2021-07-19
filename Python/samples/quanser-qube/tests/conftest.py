# Helper function for arguments for pytest, with defaults
def pytest_addoption(parser):
    parser.addoption("--acr_name", action="store", default="your_acr_name")
    parser.addoption("--brain_name", action="store", default="my_brain")
    parser.addoption("--brain_version", action="store", default=1)
    parser.addoption("--port", action="store", default=5005)
    parser.addoption("--render", action="store", default=False)
    parser.addoption("--num_iterations", action="store", default=640)
    parser.addoption("--scenario_file", action="store", default="assess_config.json")
    parser.addoption("--inkling_fname", action="store", default="selector.ink")
    parser.addoption("--simulator_package_name", action="store", default="testquanserqube")
    parser.addoption("--exported_brain_name", action="store", default="export-qq")
    parser.addoption("--chip_architecture", action="store", default="x64")