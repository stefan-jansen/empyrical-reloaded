#!/usr/bin/env python
from contextlib import contextmanager
from glob import glob
import os
from os.path import basename, exists, isfile
from pathlib import Path
from shutil import move, rmtree
from subprocess import check_call

HERE = Path(__file__).resolve(strict=True).parent
EMPYRICAL_ROOT = HERE.parent
TEMP_LOCATION = "/tmp/empyrical-doc"
TEMP_LOCATION_GLOB = TEMP_LOCATION + "/*"


@contextmanager
def removing(path):
    try:
        yield
    finally:
        rmtree(path)


def ensure_not_exists(path):
    if not exists(path):
        return
    if isfile(path):
        os.unlink(path)
    else:
        rmtree(path)


def main():
    old_dir = Path.cwd()
    print("Moving to %s." % HERE)
    os.chdir(HERE)

    try:
        print("Cleaning docs with 'make clean'")
        check_call(["make", "clean"])
        print("Building docs with 'make html'")
        check_call(["make", "html"])

        print("Clearing temp location '%s'" % TEMP_LOCATION)
        rmtree(TEMP_LOCATION, ignore_errors=True)

        with removing(TEMP_LOCATION):
            print("Copying built files to temp location.")
            move("build/html", TEMP_LOCATION)

            print("Moving to '%s'" % EMPYRICAL_ROOT)
            os.chdir(EMPYRICAL_ROOT)

            print("Checking out gh-pages branch.")
            check_call(
                [
                    "git",
                    "branch",
                    "-f",
                    "--track",
                    "gh-pages",
                    "origin/gh-pages",
                ]
            )
            check_call(["git", "checkout", "gh-pages"])
            check_call(["git", "reset", "--hard", "origin/gh-pages"])

            print("Copying built files:")
            for file_ in glob(TEMP_LOCATION_GLOB):
                base = basename(file_)

                print("%s -> %s" % (file_, base))
                ensure_not_exists(base)
                move(file_, ".")
    finally:
        os.chdir(old_dir)

    print()
    print("Updated documentation branch in directory %s" % EMPYRICAL_ROOT)
    print("If you are happy with these changes, commit and push to gh-pages.")


if __name__ == "__main__":
    main()
