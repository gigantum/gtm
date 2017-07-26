# Copyright (c) 2017 FlashX, LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import pytest
import tempfile
import os
import uuid
import shutil

from gtmlib.labmanager.build import Build


@pytest.fixture()
def setup_build_class():
    """Fixture to create a Build instance with a test image name that does not exist and cleanup after"""
    b = Build()
    b.image_name = "test-labmanager-image"

    # Make sure image doesn't exist
    if b.image_exists():
        b.remove_image("test-labmanager-image")

    yield b

    # Remove image post test if it still exists
    if b.image_exists():
        b.remove_image("test-labmanager-image")


class TestLabManagerBuild(object):
    def test_set_names(self):
        """Test getting and setting the container and image names"""
        b = Build()

        b.image_name = "my-image-13242"
        assert b.image_name == "my-image-13242"

        b.container_name = "my-image-43545"
        assert b.container_name == "my-image-43545"

    def test_get_names(self):
        """Test getting and setting the container and image names"""
        b = Build()

        assert type(b.image_name) == str
        assert type(b.container_name) == str

    def test_invalid_names(self):
        """Method to test setting invalid names"""
        b = Build()

        with pytest.raises(ValueError):
            b.image_name = "my-image-"

        with pytest.raises(ValueError):
            b.image_name = "-my-image"

        with pytest.raises(ValueError):
            b.image_name = "my-image324!!"

        with pytest.raises(ValueError):
            b.container_name = "my-image-"

        with pytest.raises(ValueError):
            b.container_name = "-my-image"

        with pytest.raises(ValueError):
            b.container_name = "my-image324!!"

    def test_build_labmanager(self, setup_build_class):
        """Method to test building a labmanager image"""
        assert setup_build_class.image_exists() is False

        # build
        setup_build_class.build_image()

        # Should now exist
        assert setup_build_class.image_exists() is True
