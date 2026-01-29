from loguru import logger

def main(argv):
    logger.warning('Skip as not implemented yet')
    return 0

if __name__ == '__main__':
    import sys
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    argv = sys.argv
    code = main(argv)
    sys.exit(code)