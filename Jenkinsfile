if (utils.scm_checkout()) return

bc0 = new BuildConfig()
bc0.nodetype = 'linux'
bc0.name = 'py36'
bc0.conda_ver = '4.6.8'
bc0.conda_packages = [
    "python=3.6"
]
bc0.build_cmds = [
    "pip install -e .",
]
bc0.test_cmds = [pytest -r sx --basetemp=test_results junitxml=results.xml]

utils.run([bc0])
