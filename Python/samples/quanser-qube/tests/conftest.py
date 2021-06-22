def pytest_addoption(parser):
    parser.addoption("--port", action="store", default=5005)
    parser.addoption("--render", action="store", default=False)
    parser.addoption("--num_iterations", action="store", default=640)
    parser.addoption("--scenario_file", action="store", default="assess_config.json")