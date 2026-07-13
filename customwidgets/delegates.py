"""Custom QStyledItemDelegate for use in QListView."""

from PyQt6.QtCore import QRect, QRectF, QSize, Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QStyle, QStyledItemDelegate

from app import IS_DARK
from models.utils.datastructs import Message


class MessageBubbleDelegate(QStyledItemDelegate):
    """Paint chat-style message bubbles, no editing supported."""

    H_MARGIN = 14
    V_MARGIN = 4
    TEXT_MARGIN = 6
    BUBBLE_RADIUS = 6
    MAX_WIDTH_RATIO = 0.40

    SENT_COLOR = QColor("#0a753e") if IS_DARK else QColor("#15843c")
    RECEIVED_COLOR = QColor("#434343") if IS_DARK else QColor("#f3f3f3")
    SYS_COLOR = QColor("#262626") if IS_DARK else QColor("#55776c")

    SENT_TEXT = QColor("#f3f3f3") if IS_DARK else QColor("#fafafa")
    RECEIVED_TEXT = QColor("#f3f3f3") if IS_DARK else QColor("#0d0d0d")
    SYS_TEXT = QColor("#f3f3f3")

    # selection highlight colours (semi‑transparent overlay)
    SELECTION_OVERLAY = QColor(0, 0, 0, 30) if IS_DARK else QColor(0, 0, 10, 50)

    def paint(self, painter: QPainter | None, option, index):
        """paint the message bubble for the item at the given index"""
        if painter is None:
            return

        message: Message | None = index.data(Qt.ItemDataRole.DisplayRole)
        if message is None:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        sender = message.sender
        text = message.text
        is_sys_message = message.is_system_message

        # format as 24-Jun-2023 14:30
        timestamp = message.sent_at.strftime("%d-%b-%Y %H:%M")

        if is_sys_message:
            max_width = option.rect.width()

        else:
            max_width = int(option.rect.width() * self.MAX_WIDTH_RATIO)

        # prepare fonts
        sender_font = QFont(option.font)
        sender_font.setBold(True)
        sender_font.setPointSizeF(10)

        body_font = option.font

        time_font = QFont(option.font)
        time_font.setPointSizeF(9)

        # prepare font metrics
        sender_fm = QFontMetrics(sender_font)
        body_fm = QFontMetrics(body_font)
        time_fm = QFontMetrics(time_font)

        # calculate the size of the text
        text_rect = body_fm.boundingRect(
            QRect(0, 0, max_width, 100_000),
            Qt.TextFlag.TextWordWrap,
            text,
        )

        # calculate the width of the sender and timestamp
        sender_width = sender_fm.horizontalAdvance(sender)
        time_width = time_fm.horizontalAdvance(timestamp)

        # bubble width is the maximum(text, sender, and timestamp) widths
        content_width = max(text_rect.width(), sender_width, time_width)

        # calculate the size of the bubble
        bubble_width = content_width + self.TEXT_MARGIN * 2
        bubble_height = (
            sender_fm.height()
            + 4
            + text_rect.height()
            + 6
            + time_fm.height()
            + self.TEXT_MARGIN * 2
        )

        # calculate the y position of the bubble
        y = option.rect.top() + self.V_MARGIN

        if message.sent:
            # left align sent messages
            x = option.rect.right() - bubble_width - self.H_MARGIN
            bubble_color = self.SENT_COLOR
            text_color = self.SENT_TEXT
            # sender and timestamp colour
            meta_color = QColor(208, 208, 208) if IS_DARK else QColor(230, 230, 230)

        elif is_sys_message:
            # right align received messages
            x = option.rect.left() + (option.rect.width() - bubble_width) // 2
            bubble_color = self.SYS_COLOR
            text_color = self.SYS_TEXT
            # sender and timestamp colour
            meta_color = QColor(220, 220, 220)

        else:
            # right align received messages
            x = option.rect.left() + self.H_MARGIN
            bubble_color = self.RECEIVED_COLOR
            text_color = self.RECEIVED_TEXT
            # sender and timestamp colour
            meta_color = QColor(180, 180, 180) if IS_DARK else QColor(85, 85, 85)

        bubble_rect = QRect(x, y, bubble_width, bubble_height)

        # row selection highlight
        if option.state & QStyle.StateFlag.State_Selected:
            # draw a subtle overlay over the entire row
            painter.fillRect(option.rect, self.SELECTION_OVERLAY)

        path = QPainterPath()
        path.addRoundedRect(QRectF(bubble_rect), self.BUBBLE_RADIUS, self.BUBBLE_RADIUS)

        # draw message bubble
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(bubble_color)
        painter.drawPath(path)

        left = bubble_rect.left() + self.TEXT_MARGIN
        # calculate the y position for the first text block (sender)
        current_y = bubble_rect.top() + self.TEXT_MARGIN

        # draw sender
        painter.setFont(sender_font)
        painter.setPen(QPen(meta_color))
        painter.drawText(
            QRect(left, current_y, content_width, sender_fm.height()),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            sender,
        )

        # increment y position for the next block (text)
        current_y += sender_fm.height() + 4

        # draw message
        painter.setFont(body_font)
        painter.setPen(QPen(text_color))
        painter.drawText(
            QRect(left, current_y, content_width, text_rect.height()),
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop
            | Qt.TextFlag.TextWordWrap,
            text,
        )

        # increment y position for the next block (timestamp)
        current_y += text_rect.height() + 6

        # draw timestamp
        painter.setFont(time_font)
        painter.setPen(QPen(meta_color))
        painter.drawText(
            QRect(left, current_y, content_width, time_fm.height()),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            timestamp,
        )

        painter.restore()

    def sizeHint(self, option, index):
        """return the size hint for the item at the given index"""
        message: Message | None = index.data(Qt.ItemDataRole.DisplayRole)
        if message is None:
            return QSize()

        max_width = int(option.rect.width() * self.MAX_WIDTH_RATIO)

        sender_font = QFont(option.font)
        sender_font.setBold(True)
        sender_font.setPointSizeF(9)

        time_font = QFont(option.font)
        time_font.setPointSizeF(8)

        sender_fm = QFontMetrics(sender_font)
        body_fm = QFontMetrics(option.font)
        time_fm = QFontMetrics(time_font)

        body_rect = body_fm.boundingRect(
            QRect(0, 0, max_width, 100_000),
            Qt.TextFlag.TextWordWrap,
            message.text,
        )

        height = (
            self.V_MARGIN * 2
            + self.TEXT_MARGIN * 2
            + sender_fm.height()
            + 4
            + body_rect.height()
            + 6
            + time_fm.height()
        )

        return QSize(option.rect.width(), height)
