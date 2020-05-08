import os
import shutil
import tempfile
import monetdbe as mdbl
import pytest


@pytest.mark.skipif(True, reason="monetdblite compatibility - not supported yet")
class TestInitialization:
    def test_double_initialization(self, initialize_monetdbe):
        with pytest.raises(mdbl.exceptions.DatabaseError):
            mdbl.init(initialize_monetdbe)

    def test_relative_initialization(self):
        tmpdir = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            mdbl.init("./relative_path")
        except Exception:
            mdbl.shutdown()
            shutil.rmtree(tmpdir)
            assert False

        res = mdbl.sql("SELECT id FROM _tables limit 10")
        mdbl.shutdown()
        os.chdir(cwd)
        shutil.rmtree(tmpdir)

        assert len(res.get('id')) == 10
