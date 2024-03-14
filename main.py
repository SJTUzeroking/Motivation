import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QCalendarWidget, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QHeaderView, QAbstractItemView
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QIcon


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
class GoalManager(QWidget):
    def __init__(self):
        super().__init__()

        self.goals = []
        self.completed_goals = []
        self.load_data()

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # Left side
        left_layout = QVBoxLayout()

        self.goal_name_input = QLineEdit()
        self.goal_name_input.setMaxLength(10)
        self.set_border_radius(self.goal_name_input) # 设置边框样式和圆角
        left_layout.addWidget(QLabel("目标名称:"))
        left_layout.addWidget(self.goal_name_input)

        self.deadline_label = QLabel()
        self.set_border_radius(self.deadline_label) # 设置边框样式和圆角
        left_layout.addWidget(QLabel("截止日期:"))
        left_layout.addWidget(self.deadline_label)

        self.calendar = QCalendarWidget()
        self.calendar.clicked[QDate].connect(self.show_deadline)
        left_layout.addWidget(self.calendar)

        times_layout = QHBoxLayout()
        self.goal_times_input = QLineEdit()
        self.goal_times_input.setMaxLength(3)
        self.set_border_radius(self.goal_times_input) # 设置边框样式和圆角
        times_layout.addWidget(QLabel("需要完成的次数:"))
        times_layout.addWidget(self.goal_times_input)
        left_layout.addLayout(times_layout)

        self.add_button = QPushButton("添加目标")
        self.add_button.clicked.connect(self.add_goal)
        self.add_button.setFixedHeight(50)
        self.set_border_radius(self.add_button)  # 设置边框样式和圆角
        left_layout.addWidget(self.add_button, alignment=Qt.AlignTop)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(350)

        # Right side
        right_layout = QVBoxLayout()

        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(4)
        self.goals_table.setHorizontalHeaderLabels(["名称", "截止时间", "完成次数", "操作"])
        right_layout.addWidget(self.goals_table)

        self.completed_goals_button = QPushButton("已完成目标")
        self.completed_goals_button.clicked.connect(self.show_completed_goals)
        self.set_border_radius(self.completed_goals_button)
        right_layout.addWidget(self.completed_goals_button)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        right_widget.setFixedWidth(650)

        # Add widgets to main layout
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)

        self.setLayout(layout)

        self.setWindowTitle("Motivation")
        self.show()
        self.setFixedHeight(600)

        self.update_goals_list()

    def show_deadline(self, date):
        self.deadline_label.setText(date.toString("yyyy-MM-dd"))

    def add_goal(self):
        goal_name = self.goal_name_input.text()
        deadline = self.deadline_label.text()
        completed_times = int(self.goal_times_input.text()) if self.goal_times_input.text() else 0

        if len(goal_name) > 10:
            QMessageBox.warning(self, "警告", "目标名称不能超过10个字符！")
            return
        if not completed_times:
            QMessageBox.warning(self, "警告", "请输入需要完成的次数！")
            return

        new_goal = {"name": goal_name, "deadline": deadline, "target_times": completed_times, "completed_times": 0}
        self.goals.append(new_goal)
        self.save_data()
        self.update_goals_list()
        self.goal_name_input.clear()
        self.deadline_label.clear()
        self.goal_times_input.clear()

    def update_goals_list(self):
        self.goals_table.setRowCount(len(self.goals))
        for row, goal in enumerate(self.goals):
            self.goals_table.setItem(row, 0, QTableWidgetItem(goal['name']))
            self.goals_table.setItem(row, 1, QTableWidgetItem(goal['deadline']))
            self.goals_table.setItem(row, 2, QTableWidgetItem(f"{goal['completed_times']}/{goal['target_times']}"))

            add_button = QPushButton()
            add_button.setIcon(QIcon(resource_path('./icons/add.png')))  # 设置图标
            add_button.clicked.connect(lambda _, g=goal: self.add_completed_times(g))

            edit_button = QPushButton()
            edit_button.setIcon(QIcon(resource_path('./icons/edit.png')))  # 设置图标
            edit_button.clicked.connect(lambda _, g=goal: self.edit_goal(g))

            delete_button = QPushButton()
            delete_button.setIcon(QIcon(resource_path('./icons/delete.png')))  # 设置图标
            delete_button.clicked.connect(lambda _, r=row: self.confirm_delete_goal(r))

            reduce_button = QPushButton()
            reduce_button.setIcon(QIcon(resource_path('./icons/undo.png')))  # 设置图标
            reduce_button.clicked.connect(lambda _, r=row: self.reduce_completed_times(r))

            btn_layout = QHBoxLayout()
            btn_layout.addWidget(add_button)
            btn_layout.addWidget(edit_button)
            btn_layout.addWidget(delete_button)
            btn_layout.addWidget(reduce_button)

            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)

            self.goals_table.setCellWidget(row, 3, btn_widget)

        column_widths = [150, 150, 80, 240]
        for i, width in enumerate(column_widths):
            self.goals_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
            self.goals_table.horizontalHeader().resizeSection(i, width)

        self.goals_table.setEditTriggers(QTableWidget.NoEditTriggers)

        for i in range(self.goals_table.rowCount()):
            self.goals_table.setRowHeight(i, 75)

        for i in range(self.goals_table.rowCount()):
            for j in range(self.goals_table.columnCount()):
                item = self.goals_table.item(i, j)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)

        self.goals_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.goals_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

    def load_data(self):
        try:
            with open("goals.json", "r") as f:
                data = json.load(f)
                self.goals = data.get('goals', [])
                self.completed_goals = data.get('completed_goals', [])
        except FileNotFoundError:
            pass

    def save_data(self):
        data = {'goals': self.goals, 'completed_goals': self.completed_goals}
        with open("goals.json", "w") as f:
            json.dump(data, f, indent=4)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '退出确认', '您确定要退出吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.save_data()
            event.accept()
        else:
            event.ignore()

    def edit_goal(self, goal):
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑目标")
        layout = QVBoxLayout()

        name_input = QLineEdit()
        name_input.setText(goal["name"])
        name_input.setMaxLength(10)  # 设置最大输入长度为10
        layout.addWidget(QLabel("目标名称:"))
        layout.addWidget(name_input)

        deadline_label = QLabel()
        deadline_label.setText(goal["deadline"])
        layout.addWidget(QLabel("截止日期:"))
        layout.addWidget(deadline_label)

        calendar = QCalendarWidget()
        calendar.clicked[QDate].connect(lambda date: deadline_label.setText(date.toString("yyyy-MM-dd")))
        layout.addWidget(calendar)

        times_input = QLineEdit()
        times_input.setText(str(goal["target_times"]))
        times_input.setMaxLength(3)  # 设置最大输入长度为3
        layout.addWidget(QLabel("需要完成的次数:"))
        layout.addWidget(times_input)

        save_button = QPushButton("保存")
        save_button.clicked.connect(
            lambda: self.save_edit_goal(goal, name_input.text(), deadline_label.text(), times_input.text(), dialog))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def save_edit_goal(self, goal, name, deadline, times, dialog):
        goal["name"] = name
        goal["deadline"] = deadline
        goal["target_times"] = int(times)
        self.update_goals_list()
        self.save_data()
        dialog.accept()

    def confirm_delete_goal(self, row):
        reply = QMessageBox.question(self, '删除确认', '您确定要删除此目标吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.delete_goal(row)

    def delete_goal(self, row):
        goal = self.goals.pop(row)
        self.update_goals_list()
        self.completed_goals.append(goal)
        self.save_data()

    def add_completed_times(self, goal):
        goal["completed_times"] += 1
        if goal["completed_times"] == goal["target_times"]:
            QMessageBox.information(self, "恭喜", "您已经完成目标：{}".format(goal["name"]))
            self.delete_goal(self.goals.index(goal))
        else:
            self.update_goals_list()
            self.save_data()

    def reduce_completed_times(self, row):
        goal = self.goals[row]
        if goal["completed_times"] > 0:
            goal["completed_times"] -= 1
            self.update_goals_list()
            self.save_data()
        else:
            QMessageBox.warning(self, "警告", "已完成次数不能再减少了！")

    def show_completed_goals(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("已完成目标列表")
        layout = QVBoxLayout()

        completed_table = QTableWidget()
        completed_table.setColumnCount(3)
        completed_table.setHorizontalHeaderLabels(["名称", "截止时间", "完成次数"])
        completed_table.setRowCount(len(self.completed_goals))
        layout.addWidget(completed_table)

        for row, goal in enumerate(self.completed_goals):
            completed_table.setItem(row, 0, QTableWidgetItem(goal['name']))
            completed_table.setItem(row, 1, QTableWidgetItem(goal['deadline']))
            completed_table.setItem(row, 2, QTableWidgetItem(str(goal['completed_times'])))

        dialog.setLayout(layout)
        dialog.exec_()

    def set_border_radius(self, widget):
        widget.setStyleSheet("border: 2px solid #008080; border-radius: 5px;") # 设置边框样式和圆角

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GoalManager()
    sys.exit(app.exec_())
