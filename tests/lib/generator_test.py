###############################################################
# pytest -v --capture=no tests/test_03_generator.py
# pytest -v  tests/test_03_generator.py
# pytest -v --capture=no  tests/test_generator..py::Test_name::<METHODNAME>
###############################################################
"""
# Headline

Here come document for test

"""
import os
import sys
import requests
sys.path.append("./tests")
import util as util
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from importlib import import_module
from cloudmesh.openapi.function.executor import Parameter
import types
from cloudmesh.common.dotdict import dotdict


class GeneratorBaseTest:

    def __init__(self,filename,all_functions,import_class):
        global globalcommandstring
        global globalbuildcommandstring
        global globalcommandparameter
        global globalbuildcommandparameter

        cmd = self.get_servercommand(filename, all_functions, import_class)
        dataforclass = self.server_dotdict(cmd)
        globalcommandparameter = Parameter(dataforclass)
        build_dotdict=self.build_dotdict()
        globalbuildcommandparameter=Parameter(build_dotdict)
        globalbuildcommandstring= self.get_build_servercommand(build_dotdict)
        print("globalbuildcommandstring  asdgafdgfadgsfdgsf ",globalbuildcommandstring)


    def get_servercommand(self,filename,all_functions,import_class) -> str:
        print(all_functions)
        serverCommand=""
        if import_class:
          serverCommand=f"cms openapi generate --filename={filename} --import_class"
        elif all_functions:
          serverCommand = f"cms openapi generate --filename={filename} --all_functions"
        return serverCommand

    def get_build_servercommand(self,build_dotdict) -> str:
        serverCommand=""
        if globalbuildcommandparameter.import_class:
          serverCommand=f"cms openapi generate {build_dotdict.FUNCTION} --filename={build_dotdict.filename} --import_class"
        elif globalbuildcommandparameter.all_functions:
          serverCommand = f"cms openapi generate --filename={build_dotdict.filename} --all_functions"

        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ ",serverCommand)
        return serverCommand

    def server_dotdict(self,serverCommand) -> dotdict:
        if serverCommand.__contains__("generate"):
            words=serverCommand.split()
            dotdictd= dotdict()
            for word in words:
                if "--import_class" in word:
                    dotdictd["import_class"] = True
                    dotdictd["all_functions"] = False
                elif "--all_functions" in word:
                    dotdictd["all_functions"] = True
                    dotdictd["import_class"] = False
                elif "--filename" in word:
                    dotdictd["filename"] = word.split("=")[1]
            return dotdictd
        if serverCommand.__contains__("server"):
           pass

    def build_dotdict(self) -> dotdict:
        dotdictd = dotdict()

        if  globalcommandparameter.import_class:
            dotdictd["import_class"] = True
            dotdictd["all_functions"] = False
            dotdictd["FUNCTION"] = globalcommandparameter.module_name.capitalize()
        elif globalcommandparameter.all_functions:
            dotdictd["all_functions"] = True
            dotdictd["import_class"] = False


        dotdictd["filename"] = globalcommandparameter.module_directory+"/build/"+globalcommandparameter.module_name+".py"


        return dotdictd


    def copy_py_file(self):
        print(globalbuildcommandparameter.module_directory)
        import os
        os.makedirs(globalcommandparameter.module_directory+"/build")
        from shutil import copyfile
        HEADING()
        Benchmark.Start()
        print(globalbuildcommandparameter.module_name)
        copyfile(globalcommandparameter.filename, globalbuildcommandparameter.filename)
        Benchmark.Stop()


    def generate(self):
        """
        function to validate paths information
        """
        HEADING()
        Benchmark.Start()
        print("5%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%555 ",globalbuildcommandstring)
        Shell.run(globalbuildcommandstring) #change variable based on your needs
        Benchmark.Stop()

    def read_spec(self):
        """
        function to check if YAML synatx is correct or not
        """
        global spec
        HEADING()
        Benchmark.Start()
        spec = util.readyaml(globalbuildcommandparameter.yamlfile)
        keys = spec.keys()
        assert "openapi" in keys
        assert "info" in keys
        assert "servers" in keys
        assert "paths" in keys

    def validate_function(self):
        """
        function to check number of functions are same in py and yaml file.
        """
        HEADING()
        Benchmark.Start()
        sys.path.append(globalbuildcommandparameter.yamldirectory)
        imported_module = import_module(globalbuildcommandparameter.module_name)
        keys = spec.get('paths')
        paths= keys.keys()
        if (globalbuildcommandparameter.all_functions is True):
            for attr_name in dir(imported_module):
                if type(getattr(imported_module, attr_name)).__name__ == 'function':
                    assert f"/{globalbuildcommandparameter.function}/{attr_name}" in paths
        if (globalbuildcommandparameter.import_class is True):
            class_obj = getattr(imported_module, globalbuildcommandparameter.function)
            for attr_name in dir(class_obj):
                attr = getattr(class_obj, attr_name)
                if isinstance(attr, types.MethodType):
                    assert f"/{globalbuildcommandparameter.function}/{attr_name}" in paths

class ServerBaseTest:

    def __init__(self, startservercommand):
        global globalstartservercommand
        globalstartservercommand =startservercommand

    def start_service(self):
        """
        function to test if the server is started and available to return
        a successful http code
        """
        HEADING()
        Benchmark.Start()
        os.system(globalstartservercommand)
        result = requests.get('http://127.0.0.1:8080/cloudmesh/ui')
        Benchmark.Stop()
        assert result.status_code == 200  # find test

    def stop_server(self):
        HEADING()

        Benchmark.Start()
        # result = Shell.execute(f"cms openapi server stop {name}", shell=True)
        os.system(f"cms openapi server stop {globalbuildcommandparameter.function}")
        Benchmark.Stop()
        gotException = False;
        try:
            result = requests.get('http://127.0.0.1:8080/cloudmesh/ui')
        except Exception as ex:
            gotException = True
        assert gotException
