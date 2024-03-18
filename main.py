import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QCalendarWidget, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QHeaderView, QListWidget, QProgressBar
from PyQt5.QtCore import QDate, Qt, QDateTime, QSize
from PyQt5.QtGui import QIcon, QPixmap


def resource_path(relative_path):
    """
    返回相对路径对应的绝对路径。

    参数：
    relative_path (str): 相对路径。

    返回值：
    str: 绝对路径。

    说明：
    如果脚本是通过 PyInstaller 打包的，将使用 PyInstaller 的特殊变量 _MEIPASS 获取程序运行时的临时目录作为基础路径；
    否则将使用脚本所在文件的目录作为基础路径。
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class GoalManager(QWidget):
    def __init__(self):
        """
        类构造函数，初始化实例属性并调用加载数据和初始化界面的方法。
        """
        super().__init__()

        # 初始化目标列表、已完成目标列表和用户操作记录列表
        self.goals = []
        self.completed_goals = []
        self.user_actions = []

        # 调用加载数据和初始化界面的方法
        self.load_data()
        self.init_ui()

    def init_ui(self):
        """
        初始化用户界面布局和组件。
        """
        layout = QHBoxLayout()  # 创建水平布局

        # 左侧布局
        left_layout = QVBoxLayout()  # 创建垂直布局

        # 目标名称输入框
        self.goal_name_input = QLineEdit()
        self.goal_name_input.setMaxLength(10)  # 设置最大长度
        self.set_border_radius(self.goal_name_input)  # 设置边框样式
        left_layout.addWidget(QLabel("目标名称:"))  # 添加标签
        left_layout.addWidget(self.goal_name_input)  # 添加输入框

        # 截止日期显示标签和日历组件
        self.deadline_label = QLabel()
        self.set_border_radius(self.deadline_label)
        left_layout.addWidget(QLabel("截止日期:"))
        left_layout.addWidget(self.deadline_label)
        self.calendar = QCalendarWidget()
        self.calendar.clicked[QDate].connect(self.show_deadline)
        left_layout.addWidget(self.calendar)

        # 需要完成的次数输入框
        times_layout = QHBoxLayout()
        self.goal_times_input = QLineEdit()
        self.goal_times_input.setMaxLength(3)  # 设置最大长度
        self.set_border_radius(self.goal_times_input)  # 设置边框样式
        times_layout.addWidget(QLabel("需要完成的次数:"))
        times_layout.addWidget(self.goal_times_input)
        left_layout.addLayout(times_layout)

        # 添加目标按钮
        self.add_button = QPushButton("添加目标")
        self.add_button.clicked.connect(self.add_goal)
        self.add_button.setFixedHeight(50)
        self.set_border_radius(self.add_button)
        left_layout.addWidget(self.add_button, alignment=Qt.AlignTop)  # 垂直布局顶部对齐

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(350)  # 设置左侧组件宽度

        # 右侧布局
        right_layout = QVBoxLayout()  # 创建垂直布局

        # 目标列表表格
        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(4)
        self.goals_table.setHorizontalHeaderLabels(["名称", "截止时间", "完成次数", "操作"])
        right_layout.addWidget(self.goals_table)

        # 按钮布局
        buttons_layout = QHBoxLayout()

        # 已完成目标按钮
        self.completed_goals_button = QPushButton()
        self.completed_goals_button.setIcon(QIcon(resource_path('./icons/complete.png')))  # 设置图标
        self.completed_goals_button.setText("已完成目标")  # 设置按钮文本
        self.completed_goals_button.clicked.connect(self.show_completed_goals)
        self.completed_goals_button.setFixedHeight(50)
        self.set_border_radius(self.completed_goals_button)
        buttons_layout.addWidget(self.completed_goals_button)

        # 目标记录按钮
        self.record_button = QPushButton()
        self.record_button.setIcon(QIcon(resource_path('./icons/rizhi.png')))  # 设置图标
        self.record_button.setText("目标记录")  # 设置按钮文本
        self.record_button.clicked.connect(self.show_user_actions)
        self.record_button.setFixedHeight(50)
        self.set_border_radius(self.record_button)
        buttons_layout.addWidget(self.record_button)

        self.logo_button = QPushButton()
        icon = QIcon(resource_path('./icons/logo.ico'))  # 设置图标
        self.logo_button.setFixedSize(50, 50)
        icon_size = QSize(50, 50)  # 设置图标大小
        self.logo_button.setIcon(icon)
        self.logo_button.setIconSize(icon_size)
        self.logo_button.setStyleSheet("background-color: transparent; border: none;")
        self.logo_button.clicked.connect(self.show_logo)
        buttons_layout.addWidget(self.logo_button)

        right_layout.addLayout(buttons_layout)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        right_widget.setFixedWidth(700)  # 设置右侧组件宽度

        # 将左侧和右侧组件添加到主布局
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)

        self.setLayout(layout)  # 设置窗口布局
        self.setWindowTitle("Motivation")  # 设置窗口标题
        self.show()  # 显示窗口
        self.setFixedHeight(600)  # 设置窗口初始高度
        self.update_goals_list()  # 更新目标列表显示

    def show_deadline(self, date):
        self.deadline_label.setText(date.toString("yyyy-MM-dd"))

    def set_border_radius(self, widget):
        widget.setStyleSheet("border: 2px solid #5171F0; border-radius: 5px;")  # 设置边框样式和圆角

    def update_goals_list(self):
        """
        更新目标列表显示。

        说明：
        根据当前的目标数据，更新目标列表的显示内容和操作按钮。
        """
        self.goals_table.setRowCount(len(self.goals))
        for row, goal in enumerate(self.goals):
            self.goals_table.setItem(row, 0, QTableWidgetItem(goal['name']))
            self.goals_table.setItem(row, 1, QTableWidgetItem(goal['deadline']))
            self.goals_table.setItem(row, 2, QTableWidgetItem(f"{goal['completed_times']}/{goal['target_times']}"))

            # 添加操作按钮
            add_button = QPushButton()
            add_button.setIcon(QIcon(resource_path('./icons/add.png')))  # 设置图标
            add_button.clicked.connect(lambda _, g=goal: self.add_completed_times(g))
            add_button.setFixedWidth(50)

            edit_button = QPushButton()
            edit_button.setIcon(QIcon(resource_path('./icons/edit.png')))  # 设置图标
            edit_button.clicked.connect(lambda _, g=goal: self.edit_goal(g))
            edit_button.setFixedWidth(50)

            delete_button = QPushButton()
            delete_button.setIcon(QIcon(resource_path('./icons/delete.png')))  # 设置图标
            delete_button.clicked.connect(lambda _, g=goal: self.confirm_delete_goal(g))
            delete_button.setFixedWidth(50)

            reduce_button = QPushButton()
            reduce_button.setIcon(QIcon(resource_path('./icons/undo.png')))  # 设置图标
            reduce_button.clicked.connect(lambda _, g=goal: self.reduce_completed_times(g))
            reduce_button.setFixedWidth(50)

            # 创建进度条
            progress_bar = QProgressBar()
            progress_bar.setRange(0, goal['target_times'])  # 设置进度条范围
            progress_bar.setValue(goal['completed_times'])  # 设置进度条当前值
            progress_bar.setFormat(f"{goal['completed_times']}/{goal['target_times']}")  # 设置进度条上方文字显示
            progress_bar.setFixedWidth(80)  # 设置进度条的默认长度

            # 将操作按钮和进度条放置在水平布局中
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(add_button)
            btn_layout.addWidget(edit_button)
            btn_layout.addWidget(delete_button)
            btn_layout.addWidget(reduce_button)
            btn_layout.addWidget(progress_bar)

            btn_widget = QWidget()
            btn_widget.setLayout(btn_layout)

            # 将操作按钮和进度条添加到表格的单元格中
            self.goals_table.setCellWidget(row, 3, btn_widget)

        # 设置表格列宽
        column_widths = [130, 130, 70, 320]
        for i, width in enumerate(column_widths):
            self.goals_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
            self.goals_table.horizontalHeader().resizeSection(i, width)

        # 禁止编辑表格内容
        self.goals_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 设置表格行高和内容居中显示
        for i in range(self.goals_table.rowCount()):
            self.goals_table.setRowHeight(i, 75)
            for j in range(self.goals_table.columnCount()):
                item = self.goals_table.item(i, j)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)

    def load_data(self):
        """
        加载数据并更新实例属性。

        说明：
        尝试从文件 "goals.json" 中加载数据，更新目标列表、已完成目标列表和用户操作记录列表。
        如果文件不存在，则忽略异常。
        """
        try:
            with open("goals.json", "r") as f:
                data = json.load(f)
                self.goals = data.get('goals', [])
                self.completed_goals = data.get('completed_goals', [])
                self.user_actions = data.get('user_actions', [])
        except FileNotFoundError:
            pass

    def save_data(self):
        """
        保存数据到文件 "goals.json"。

        说明：
        将目标列表、已完成目标列表和用户操作记录列表保存为 JSON 格式，并写入到文件 "goals.json" 中。
        """
        data = {'goals': self.goals, 'completed_goals': self.completed_goals, 'user_actions': self.user_actions}
        with open("goals.json", "w") as f:
            json.dump(data, f, indent=4)

    def add_goal(self):
        """
        添加新目标。

        说明：
        从用户输入中获取目标名称、截止日期和需要完成的次数，进行输入验证。
        如果输入合法，则创建新目标并添加到目标列表中，并更新目标列表显示。
        同时记录用户的操作，记录格式为 "你在{时间}添加了目标{目标名称}"。
        """
        goal_name = self.goal_name_input.text().strip()  # 去除首尾空格
        deadline = self.deadline_label.text()
        completed_times_str = self.goal_times_input.text()

        # 输入验证
        if not goal_name:
            QMessageBox.warning(self, "警告", "请输入目标名称！")
            return
        if len(goal_name) > 10:
            QMessageBox.warning(self, "警告", "目标名称不能超过10个字符！")
            return
        if not completed_times_str:
            QMessageBox.warning(self, "警告", "请输入需要完成的次数！")
            return
        try:
            completed_times = int(completed_times_str)
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的次数！")
            return
        if completed_times < 1:
            QMessageBox.warning(self, "警告", "目标次数不能小于1次！")
            return

        # 创建新目标并添加到目标列表
        new_goal = {"name": goal_name, "deadline": deadline, "target_times": completed_times, "completed_times": 0}
        self.goals.append(new_goal)
        self.update_goals_list()
        self.goal_name_input.clear()
        self.deadline_label.clear()
        self.goal_times_input.clear()

        # 记录用户操作
        action_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm")
        self.user_actions.insert(0, f"你在{action_time}添加了目标【{goal_name}】")
        self.save_data()

    def edit_goal(self, goal):
        """
        编辑目标信息。

        参数：
        goal (dict): 要编辑的目标。

        说明：
        打开一个对话框，允许用户编辑目标的名称、截止日期和需要完成的次数。
        用户点击保存按钮后，调用保存编辑目标的方法。
        """
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

    def save_edit_goal(self, goal, new_name, new_deadline, new_times, dialog):
        """
        保存编辑后的目标信息。

        参数：
        goal (dict): 要保存的目标。
        new_name (str): 编辑后的目标名称。
        new_deadline (str): 编辑后的截止日期。
        new_times (str): 编辑后的需要完成的次数。
        dialog (QDialog): 编辑目标的对话框。

        说明：
        验证编辑后的目标名称和需要完成的次数的合法性，如果合法则更新目标信息并保存。
        同时记录用户的操作，记录格式为 "你在{时间}将目标【旧名称】【旧截止日期】【旧次数】修改为【新名称】【新截止日期】【新次数】"。
        """
        if not new_name.strip():
            QMessageBox.warning(dialog, "警告", "请输入目标名称！")
            return
        if len(new_name) > 10:
            QMessageBox.warning(dialog, "警告", "目标名称不能超过10个字符！")
            return
        try:
            target_times = int(new_times)
        except ValueError:
            QMessageBox.warning(dialog, "警告", "请输入有效的次数！")
            return
        if int(new_times) < 1:
            QMessageBox.warning(dialog, "警告", "目标次数不能小于1次！")
            return

        old_name = goal["name"]
        old_deadline = goal["deadline"]
        old_times = goal["target_times"]

        goal["name"] = new_name
        goal["deadline"] = new_deadline
        goal["target_times"] = target_times
        self.update_goals_list()
        dialog.accept()

        # 记录用户操作
        action_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm")
        action_str = f"你在{action_time}将目标【{old_name}】【{old_deadline}】【{old_times}】修改为【{new_name}】【{new_deadline}】【{target_times}】"
        self.user_actions.insert(0, action_str)
        self.save_data()

    def confirm_delete_goal(self, goal):
        """
        确认删除目标。

        参数：
        goal (dict): 要删除的目标对象。

        说明：
        弹出对话框以确认用户是否要删除目标。
        如果用户确认删除，则调用删除目标的方法。
        """
        reply = QMessageBox.question(self, '删除确认', '您确定要删除此目标吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.delete_goal(goal)

    def delete_goal(self, goal):
        """
        删除目标。

        参数：
        goal (dict): 要删除的目标对象。

        说明：
        从目标列表中删除指定索引的目标，并更新目标列表显示。
        同时记录用户的操作，记录格式为 "你在{时间}删除了目标{目标名称}"。
        """
        self.goals.remove(goal)
        self.update_goals_list()

        # 记录用户操作
        action_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm")
        self.user_actions.insert(0, f"你在{action_time}删除了目标【{goal['name']}】")
        self.save_data()

    def add_completed_times(self, goal):
        """
        增加目标的完成次数。

        参数：
        goal (dict): 要增加完成次数的目标。

        说明：
        增加目标的完成次数，如果完成次数达到目标设定的次数，则提示用户已完成目标，并记录目标的完成日期。
        同时更新目标列表显示和保存数据。
        记录用户的操作，记录格式为 "你在{时间}完成了目标{目标名称}"。
        """
        goal["completed_times"] += 1
        if goal["completed_times"] == goal["target_times"]:
            QMessageBox.information(self, "恭喜", "您已经完成目标：{}".format(goal["name"]))
            goal["completion_date"] = QDate.currentDate().toString("yyyy-MM-dd")  # 记录目标完成日期
            self.completed_goals.append(goal)
            self.delete_goal(goal)
        else:
            self.update_goals_list()

        # 记录用户操作
        action_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm")
        self.user_actions.insert(0, f"你在{action_time}完成了目标【{goal['name']}】")
        self.save_data()

    def reduce_completed_times(self, goal):
        """
        减少目标的完成次数。

        参数：
        goal (dict): 要删除的目标对象。

        说明：
        减少目标的完成次数，如果已完成次数大于0，则更新目标列表显示和保存数据。
        否则弹出警告提示已完成次数不能再减少。
        同时记录用户的操作，记录格式为 "你在{时间}撤销完成了目标{目标名称}"。
        """
        if goal["completed_times"] > 0:
            goal["completed_times"] -= 1
            self.update_goals_list()
        else:
            QMessageBox.warning(self, "警告", "已完成次数不能再减少了！")

        # 记录用户操作
        action_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm")
        self.user_actions.insert(0, f"你在{action_time}撤销完成了目标【{goal['name']}】")
        self.save_data()

    def show_completed_goals(self):
        """
        显示已完成目标列表。

        说明：
        弹出对话框展示已完成目标列表，包括目标的名称、截止时间、完成次数和完成日期。
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("已完成目标列表")
        layout = QVBoxLayout()

        completed_table = QTableWidget()
        completed_table.setColumnCount(4)
        completed_table.setHorizontalHeaderLabels(["名称", "截止时间", "完成次数", "完成日期"])
        completed_table.setRowCount(len(self.completed_goals))
        layout.addWidget(completed_table)

        for row, goal in enumerate(self.completed_goals):
            completed_table.setItem(row, 0, QTableWidgetItem(goal['name']))
            completed_table.setItem(row, 1, QTableWidgetItem(goal['deadline']))
            completed_table.setItem(row, 2, QTableWidgetItem(str(goal['completed_times'])))
            if 'completion_date' in goal:
                completed_table.setItem(row, 3, QTableWidgetItem(goal['completion_date']))

        # 设置单元格内容居中显示
        for i in range(completed_table.rowCount()):
            for j in range(completed_table.columnCount()):
                item = completed_table.item(i, j)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
        dialog.setLayout(layout)
        dialog.resize(500, 400)
        dialog.exec_()

    def show_user_actions(self):
        """
        显示用户的操作记录。

        说明：
        弹出对话框展示用户的操作记录，以列表形式呈现。
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("目标记录")
        layout = QVBoxLayout()

        actions_list = QListWidget()
        actions_list.addItems(self.user_actions)  # 将操作记录添加到列表中
        layout.addWidget(actions_list)

        dialog.setLayout(layout)
        dialog.resize(700, 450)
        dialog.exec_()

    def show_logo(self):
        dialog = QDialog()
        dialog.setWindowTitle("About")
        dialog.setWindowIcon(QIcon(resource_path('./icons/logo.ico')))
        layout = QVBoxLayout(dialog)

        # 添加程序logo
        logo_label = QLabel(dialog)
        logo_pixmap = QPixmap(resource_path('./icons/logo.ico')).scaledToWidth(100)
        logo_label.setPixmap(logo_pixmap)
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # 添加GitHub链接
        github_label = QLabel("<a href='https://github.com/SJTUzeroking'>GitHub</a>", dialog)
        github_label.setOpenExternalLinks(True)
        layout.addWidget(github_label, alignment=Qt.AlignCenter)

        # 添加作者信息
        author_label = QLabel("Developed By Zou Ruoqin", dialog)
        layout.addWidget(author_label, alignment=Qt.AlignCenter)

        dialog.setLayout(layout)
        dialog.resize(300, 150)
        dialog.exec_()

    def closeEvent(self, event):
        """
        关闭窗口时的事件处理。

        参数：
        event (QCloseEvent): 关闭事件对象。

        说明：
        当窗口关闭时，弹出对话框询问用户是否确认退出。如果用户确认退出，则保存数据并关闭窗口，否则忽略关闭事件。
        """
        reply = QMessageBox.question(self, '退出确认', '您确定要退出吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.save_data()
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GoalManager()
    sys.exit(app.exec_())
