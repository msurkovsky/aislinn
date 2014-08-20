
from utils import TestCase
import unittest

class CollectiveTests(TestCase):

    category = "collective"

    def test_invalid(self):
        self.program("invalid")

        args = [ "gatherv_root",
                 "gatherv_sendcount",
                 "reduce_op" ]

        for arg in args:
            self.execute(2, (arg,))
            self.single_error("invalidarg", rank=0)

    def test_ibarrier(self):
        self.program("ibarrier")

        def check_output1(output):
            self.assertEquals(set(output.strip().split("\n")),
                              set(["a = 0; b = 200", "a = 200; b = 0"]))
        def check_output2(output):
            self.assertEquals(set(output.strip().split("\n")), set(["a = 0; b = 200"]))

        self.execute(3, "a", stdout=check_output1)
        self.no_errors()
        self.execute(3, "b", stdout=check_output2)
        self.no_errors()

    def test_gatherv(self):
        output1 = "OUT1: 100 101\n" \
                  "OUT2: 100 101\n"
        output3 = "OUT1: 100 101 102 103 104 105 200 201 202 203 204 300 301 302 303\n"\
                  "OUT2: 100 101 102 103 104 105 200 201 202 203 204 300 301 302 303\n"
        self.program("gatherv")

        self.execute(1, "waitall", stdout=output1)
        self.no_errors()
        self.execute(3, "waitall", stdout=output3)
        self.no_errors()

        self.execute(1, "wait", stdout=output1)
        self.no_errors()
        self.execute(3, "wait", stdout=output3)
        self.no_errors()

        self.execute(3, "mismatch")
        self.single_error("rootmismatch")

    def test_igather(self):
        output = "OUT1: 100 101 102 103 200 201 202 203 300 301 302 303\n" \
                 "OUT2: 1000 1001 1002 1003 2000 2001 2002 2003 3000 3001 3002 3003\n"
        self.program("igather")
        self.execute(3, "0", stdout=output)
        self.no_errors()
        self.execute(3, "1", stdout=output)
        self.no_errors()
        self.execute(3, "2", stdout=output)
        self.no_errors()

    def test_iscatterv(self):
        output1 = "0/2:OUT1: 100 200\n" \
                  "0/2:OUT2: 100 200\n"

        output3 = "0/6:OUT1: 100 200 300 400 500 600\n" \
                  "0/6:OUT2: 100 200 300 400 500 600\n" \
                  "1/5:OUT1: 200 300 400 500 600\n" \
                  "1/5:OUT2: 200 300 400 500 600\n" \
                  "2/4:OUT1: 300 400 500 600\n" \
                  "2/4:OUT2: 300 400 500 600\n"

        self.program("iscatterv")
        self.execute(1, "waitall", stdout=output1)
        self.no_errors()

        self.program("iscatterv")
        self.execute(3, "waitall", stdout=output3)
        self.no_errors()

        self.program("iscatterv")
        self.execute(1, "wait", stdout=output1)
        self.no_errors()

        self.program("iscatterv")
        self.execute(3, "wait", stdout=output3)
        self.no_errors()

    def test_iscatter(self):
        output = "0: OUT1: 100 200 300 400\n" \
                 "0 OUT2: 1000 2000 3000 4000\n" \
                 "1: OUT1: 500 600 700 800\n" \
                 "1 OUT2: 5000 6000 7000 8000\n" \
                 "2: OUT1: 900 1000 1100 1200\n" \
                 "2 OUT2: 9000 10000 11000 12000\n"

        self.program("iscatter")
        self.execute(3, "0", stdout=output, vgv=0)
        self.no_errors()
        self.execute(3, "1", stdout=output)
        self.no_errors()
        self.execute(3, "2", stdout=output)
        self.no_errors()

    def test_reduce(self):
        output = "OUT1: 600 603 606 609\n" \
                 "OUT2: 6000000 6110601 6222408 6335427\n" \
                 "OUT1d: 0.6 0.603 0.606 0.609\n" \
                 "OUT2d: 0.006 0.0061106 0.00622241 0.00633543\n"
        self.program("reduce")

        self.execute(3, "ok", stdout=output)
        self.no_errors()

    def test_allreduce(self):
        output = "OUT1: 600 603 606 609\n" \
                 "OUT2: 6000000 6110601 6222408 6335427\n" \
                 "OUT1d: 0.6 0.603 0.606 0.609\n" \
                 "OUT2d: 0.006 0.0061106 0.00622241 0.00633543\n"
        self.program("allreduce")

        self.execute(3, "ok", stdout=output * 3)
        self.no_errors()

    def test_loc(self):
        output = "int: (100, 1) (100, 1)\n" \
                 "int: (100, 3) (300, 30)\n" \
                 "int: (1, 3) (3, -5)\n" \
                 "double: (0.1, 1) (0.1, 1)\n" \
                 "double: (0.1, 3) (0.3, 30)\n" \
                 "double: (0.001, 3) (0.003, -5)\n"
        self.program("loc")
        self.execute(3, "ok", stdout=output)
        self.no_errors()


if __name__ == "__main__":
    unittest.main()
