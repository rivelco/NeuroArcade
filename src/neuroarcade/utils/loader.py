import pkgutil
import importlib
import inspect


def discover_classes(package_name: str) -> dict:
    """Function used to discover classes for games, controls and transformers.
    
    Discover classes where:
      - file name == class name
      - class is defined in that file

    Args:
        package_name (str): The expected name of the package.

    Returns:
        dict: Dictionary mapping the name of the module with the callable module.
    """
    classes = {}

    package = importlib.import_module(package_name)

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package_name}.{module_name}")

        # Expect class with same name as file
        if hasattr(module, module_name):
            cls = getattr(module, module_name)

            if inspect.isclass(cls) and cls.__module__ == module.__name__:
                classes[module_name] = cls

    return classes
