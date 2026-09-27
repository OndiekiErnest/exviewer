"""App utility functions."""

from pathlib import Path
from shutil import rmtree
from zipfile import BadZipFile, ZipFile

import orjson

from constants import TEMP_DIR


def is_zip_encrypted(zip_path):
    """check if a zip file is password-protected"""
    try:
        with ZipFile(zip_path, "r") as zf:
            for zinfo in zf.infolist():
                # check if the first bit (0x1) is set in flag_bits
                if zinfo.flag_bits & 0x1:
                    return True

    except BadZipFile:
        return False

    return False


def textfile_from_zip(zip_path: Path, pwd: bytes | None = None):
    """extract all files from a zip file to the temp dir and return a text (.txt) file path"""
    # create extract folder in temp dir using zip name
    extract_path = Path(TEMP_DIR) / zip_path.stem

    if not extract_path.exists():
        extract_path.mkdir(parents=True, exist_ok=True)

        with ZipFile(zip_path) as zip_ref:
            zip_ref.extractall(extract_path, pwd=pwd)

    for file in extract_path.iterdir():
        if file.suffix == ".txt":
            return file

    raise ValueError("No text file found in zip")


def remove_temp_dir():
    """remove the temp directory"""
    rmtree(TEMP_DIR, ignore_errors=True)


def read_json(json_file: str):
    """read and return contents of json file, doesn't handle exceptions"""
    with open(json_file, "rb") as file:
        return orjson.loads(file.read())


def save_json(json_file: str, data: dict | list):
    """save data to json file, doesn't handle exceptions"""
    with open(json_file, "wb") as file:
        serialized = orjson.dumps(data, option=orjson.OPT_INDENT_2)
        file.write(serialized)
