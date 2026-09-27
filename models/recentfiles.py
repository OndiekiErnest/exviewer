"""App data models."""

import logging
import os

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt

from datastructs import FileInfo
from utils import read_json, save_json
from constants import RECENT_FILES_PATH

logger = logging.getLogger(__name__)


class FilesListModel(QAbstractListModel):
    """Model for displaying file base names and paths as tooltips."""

    LIMIT = 25  # maximum number of files to remember, discard old ones

    def __init__(self, *args, files: list[FileInfo] | None = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.files_list: list[FileInfo] = files[: self.LIMIT] if files else []

    def __str__(self):
        return f"FilesListModel({len(self.files_list)} files)"

    def __len__(self):
        return len(self.files_list)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """return the number of rows in the model"""
        return len(self.files_list)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        """return the data for the given index and role"""
        if not index.isValid():
            return

        if role == Qt.ItemDataRole.DisplayRole:
            return self.files_list[index.row()].name

        elif role == Qt.ItemDataRole.ToolTipRole:
            return self.files_list[index.row()].path

    def removeRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        """remove a row from the model"""
        if 0 <= row < len(self.files_list):
            self.beginRemoveRows(parent, row, row)
            del self.files_list[row]
            self.endRemoveRows()
            return True

        return False

    def removeRows(
        self, row: int, count: int, parent: QModelIndex = QModelIndex()
    ) -> bool:
        """remove multiple rows from the model"""
        if (
            0 <= row < len(self.files_list)
            and count > 0
            and (row + count) <= len(self.files_list)
        ):
            self.beginRemoveRows(parent, row, row + count - 1)
            del self.files_list[row : row + count]
            self.endRemoveRows()
            return True

        return False

    def removeRandom(self, indexes: set[int]):
        """remove multiple rows from the model based on a set of indexes"""

        sorted_indexes = sorted(indexes, reverse=True)
        for index in sorted_indexes:
            self.removeRow(index)

    def add_file(self, filename: str):
        """create a FileInfo and add it to the model"""
        file_info = FileInfo(
            name=os.path.basename(filename),
            path=filename,
            progress=0,
        )
        if not os.path.exists(filename):
            return

        if file_info in self.files_list:
            return  # already in the list, do not add again

        row = self.rowCount()
        self.beginInsertRows(QModelIndex(), row, row)

        self.files_list.append(file_info)

        self.endInsertRows()

        # remove oldest file if limit exceeded
        if len(self.files_list) > self.LIMIT:
            self.removeRow(0)

    def remove_file(self, file_info: FileInfo):
        """remove a FileInfo from the model"""
        if file_info in self.files_list:
            index = self.files_list.index(file_info)
            self.beginRemoveRows(QModelIndex(), index, index)
            self.files_list.remove(file_info)
            self.endRemoveRows()

        else:
            logger.warning(f"FileInfo {file_info} not found in model")

    def get_file(self, filename: str):
        """return the FileInfo for the given filename, if it exists in the model"""
        for file_info in self.files_list:
            if file_info.path == filename:
                logger.debug(f"get found FileInfo {file_info}")
                return file_info

    def at_index(self, index: int):
        """return the FileInfo at the given index"""
        if 0 <= index < len(self.files_list):
            return self.files_list[index]

        else:
            logger.warning(f"index {index} out of range for model")

    def update_progress(self, filename: str, progress: int):
        """update the progress of a file in the model"""

        for index, file_info in enumerate(self.files_list):
            if file_info.path == filename:
                file_info.progress = progress

                model_index = self.index(index)
                self.dataChanged.emit(
                    model_index, model_index, [Qt.ItemDataRole.DisplayRole]
                )
                logger.debug(f"Updated progress for {filename!r} to {progress}")
                return

    def from_list(self, files: list[dict]):
        """add multiple files from a list of dicts (serialized earlier) to the model"""
        exists = os.path.exists

        for details in files:
            try:
                file_info = FileInfo.from_dict(details)

            except KeyError:
                logger.warning(f"Invalid file details: {details}")
                continue

            if exists(file_info.path):
                if file_info not in self.files_list:
                    row = self.rowCount()
                    self.beginInsertRows(QModelIndex(), row, row)
                    self.files_list.append(file_info)
                    self.endInsertRows()

                    # if limit exceeded, remove oldest file
                    if len(self.files_list) > self.LIMIT:
                        self.removeRow(0)

    def to_list(self):
        """serialize the model to a list of dicts"""

        return [file_info.to_dict() for file_info in self.files_list]

    def save_to_file(self, filename: str = RECENT_FILES_PATH):
        """save the model to a json file"""

        try:
            save_json(filename, self.to_list())
            logger.debug(f"Saved {len(self.files_list)} files to {filename!r}")

        except Exception as e:
            logger.exception(e)

    def load_from_file(self, filename: str = RECENT_FILES_PATH):
        """load the model from a json file"""

        if not os.path.exists(filename):
            logger.debug(f"No recent files found at {filename!r}")
            return

        try:
            files = read_json(filename)
            self.from_list(files)
            logger.debug(f"Loaded {len(self.files_list)} files from {filename!r}")

        except Exception as e:
            logger.exception(e)

    def clear_files(self):
        """clear all FileInfo objects from the model"""
        self.beginResetModel()
        self.files_list.clear()
        self.endResetModel()


recent_files_model = FilesListModel()
recent_files_model.load_from_file()
