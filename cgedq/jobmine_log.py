
import logging
import sys
from cgedq.mine import mineJobStatesByRange

def main():
    logging.basicConfig(level=logging.INFO)
    tag = sys.argv[1]
    # noise = 0.0005
    noise = 0.002
    mineJobStatesByRange('var',tag,noise,years=[10,15,20])
    #mineJobStatesByRange('var',tag,noise,years=[10])


if __name__ == '__main__':
    main()

