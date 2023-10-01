import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import math


class Rand48:
    def __init__(self, seed, lambda_, upper_limit):
        self.seed = seed
        self.lambda_ = lambda_
        self.upper_limit = upper_limit
        self.n = (seed << 16) + 0x330e

    def next(self):
        self.n = (25214903917 * self.n + 11) & (2 ** 48 - 1)
        return self.n

    def drand(self):
        return self.next() / (2 ** 48)

    def floor(self):
        result = math.floor(-math.log(self.drand()) / self.lambda_)
        while result > self.upper_limit:
            result = math.floor(-math.log(self.drand()) / self.lambda_)
        return result

    def ceil(self):
        result = math.ceil(-math.log(self.drand()) / self.lambda_)
        while result > self.upper_limit:
            result = math.ceil(-math.log(self.drand()) / self.lambda_)
        return result

    def num_cpu(self):
        result = math.ceil(self.drand() * 64)
        return result