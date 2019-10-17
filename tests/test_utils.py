from unittest import main, TestCase
from getgauge.util import get_step_impl_dirs
import os


class UtilTests(TestCase):

    def test_get_step_impl_gives_default_if_no_env_Set(self):
        dirs = get_step_impl_dirs()
        expected = ['step_impl']
        self.assertEqual(dirs,expected)

    def test_get_step_impl_returns_array_of_impl_dirs(self):
        os.environ["STEP_IMPL_DIR"] = "step_impl, step_impl1"
        dirs = get_step_impl_dirs()
        expected = ['step_impl','step_impl1']
        self.assertEqual(dirs,expected)

    def test_get_step_impl_returns_normalized_impl_dirs_path(self):
        os.environ["STEP_IMPL_DIR"] =  "test\\step_impl" if os.path.sep == '/' else "test/step_impl"
        dirs = get_step_impl_dirs()
        expected = ["test" + os.path.sep +"step_impl"]
        self.assertEqual(dirs,expected)

if __name__ == '__main__':
    main()