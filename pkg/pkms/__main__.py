from . import main

if __name__ == '__main__':
    import sys
    argv = sys.argv
    code = main(argv)
    sys.exit(code)