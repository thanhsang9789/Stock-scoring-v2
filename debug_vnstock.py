import vnstock
import pkgutil
import sys

def find_function(package, func_name):
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        try:
            # Silence stdout/stderr during import
            # save_stdout = sys.stdout
            # sys.stdout = open(os.devnull, 'w')
            __import__(module_name)
            mod = sys.modules[module_name]
            # sys.stdout = save_stdout
            if func_name in dir(mod):
                print(f"Found '{func_name}' in {module_name}")
        except Exception as e:
            pass

print(f"Searching in vnstock v{getattr(vnstock, '__version__', 'unknown')}...")
find_function(vnstock, 'stock_historical_data')
find_function(vnstock, 'listing_companies')
find_function(vnstock, 'financial_flow')
