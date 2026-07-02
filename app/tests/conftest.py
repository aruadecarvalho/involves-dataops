import os
import tempfile

os.environ.setdefault("PIPELINE_OUTPUT_DIR", tempfile.mkdtemp(prefix="pipeline-test-"))
