# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""
    Usage of Arepyextras Test to create a new Local Dataset
    
    Use this script to create a new dataset at dataset_directory starting from data collected in source_directory.

    Each file that need to be added to the dataset must be specified as a relative path with respect to the source
    directory in a push call like the following, after instantiating the FileManager. The destination subdirectory must
    also be specified relative to the dataset directory folder that will be created.

    manager.push(
        srcdir.joinpath("relative_path/to_the_file/to_be_added/to_dataset"),
        "path_of_the_folder/relative_to/source_directory/where_this_file/will_be_placed",
        preserve_filename=True,
        overwrite_ok=True,
        readonly=True
    )

    Few flags are available to customize the push to the dataset:
    - preserve_filename: will keep the exact name of the file to be pushed, this is useful when moving product folder or
    file that must not change filenam.
    - overwrite_ok: this helps in generating the dataset to overwrite existing files if already there
    - readonly: this flag will affect usage of the Test environment later during integration tests. If True, when the
    Pull request will be performed from dataset this file will not be copied in a temporary folder to be processed but
    a symbolic link will be created: this will make the process faster and easier and the file cannot be changed by the
    user during the test. False instead will allow the copy of the "master" file and enable the user to edit it at will.

"""

from collections import namedtuple
from pathlib import Path
from typing import List

from arepyextras.test.data import FileDataManager

PushRequest = namedtuple("PushRequest", "src_rel_path dst_rel_path preserve_filename_flag overwrite_flag readonly_flag")


def create_dataset(srcdir: Path, dstdir: Path, push_requests: List[PushRequest]):
    """Function to generate a local dataset for Arepyextras Test.

    Parameters
    ----------
    srcdir : Path
        path to the source directory where files to be pushed to dataset are placed
    dstdir : Path
        path to the directory where dataset will be created
    push_requests : List[PushRequest]
        list of PushRequest elements to be executed by the manager
    """

    dstdir.mkdir(exist_ok=True)
    manager = FileDataManager("file:///" + str(dstdir))

    for request in push_requests:
        manager.push(
            srcdir.joinpath(request.src_rel_path),
            request.dst_rel_path,
            preserve_filename=request.preserve_filename_flag,
            overwrite_ok=request.overwrite_flag,
            readonly=request.readonly_flag,
        )
