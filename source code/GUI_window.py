from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QPushButton, QFileDialog, QLabel, QScrollArea, QWidget, QVBoxLayout, QRadioButton, QGroupBox, QProgressBar, QTextEdit, QDialog, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QWaitCondition
from PyQt5.QtGui import QPixmap, QFont, QIcon
import img_cropper
import time
import os
import sys
import ctypes

class ProcessorThread(QThread):
    progress_updated = pyqtSignal(int)
    update_info = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, input_file_paths, input_folder_path, output_folder_path, is_alpha, is_chinese):
        super().__init__()

        self.is_running = True
        self.is_paused = False
        self.is_alpha = is_alpha
        self.is_chinese = is_chinese
        self.mutex = QMutex()
        self.condition = QWaitCondition()

        self.input_file_paths = input_file_paths
        self.input_folder_path = input_folder_path
        self.output_folder_path = output_folder_path


    def run(self):
        t1 = time.time()
        outpath = self.input_folder_path + '/output'
        if (self.output_folder_path == ''):
            if os.path.exists(outpath):
                pass
            else:
                os.mkdir(outpath)
        else:
            outpath = self.output_folder_path

        for file_path in self.input_file_paths:
            
            if not self.is_running:
                break

            self.mutex.lock()
            if self.is_paused:
                self.condition.wait(self.mutex)
            self.mutex.unlock()

            if self.is_alpha:
                cropped_img, ini_size, cropped_size = img_cropper.crop_by_alpha(file_path)
            else:
                cropped_img, ini_size, cropped_size = img_cropper.crop_by_white(file_path)

            temp_name = file_path.split('.')[-2].split('/')[-1]

            # 找不到图像
            if len(cropped_img) == 0:
                if self.is_chinese:
                    self.update_info.emit(f'- 找不到图像 [{temp_name}]')
                else:
                    self.update_info.emit(f'- Cannot find image [{temp_name}]')
                continue

            # 图像未被处理
            if cropped_size == ini_size:
                if self.is_chinese:
                    self.update_info.emit(f'- 图像 [{temp_name}] 未被裁剪')
                else:
                    self.update_info.emit(f'- Image [{temp_name}] is not cropped')
                continue
            
            img_cropper.file_save(cropped_img, outpath, temp_name)
            self.progress_updated.emit(100 * (self.input_file_paths.index(file_path) + 1) // len(self.input_file_paths))

            if self.is_chinese:
                self.update_info.emit(f'- 处理完成 [{temp_name}], 尺寸从 ({ini_size[0]}, {ini_size[1]}) 缩小至 ({cropped_size[0]}, {cropped_size[1]})')
            else:
                self.update_info.emit(f'- Processing of image [{temp_name}] completed, with dimensions reduced from ({ini_size[0]}, {ini_size[1]}) to ({cropped_size[0]}, {cropped_size[1]})')
        
        self.progress_updated.emit(100)
        self.finished.emit()
        if self.is_chinese:
            self.update_info.emit(f'- 文件夹 [{self.input_folder_path}] 处理完毕, 耗时 {time.time() - t1} 秒')
        else:
            self.update_info.emit(f'- Processing of folder [{self.input_folder_path}] completed, took {time.time() - t1} seconds')
        
        self.is_running = False
        self.is_paused = False


    def pause(self):
        self.mutex.lock()
        self.is_paused = True
        self.mutex.unlock()
        

    def resume(self):
        self.mutex.lock()
        self.is_paused = False
        self.condition.wakeAll()
        self.mutex.unlock()


    def cease(self):
        self.mutex.lock()
        self.is_running = False
        if self.is_paused:
            self.is_paused = False
            self.condition.wakeAll()
        self.mutex.unlock()

    def change_lang(self):
        self.is_chinese = not self.is_chinese


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)


    def mousePressEvent(self, event):
        text_rect = self.rect()
        if text_rect.contains(event.pos()):
            self.clicked.emit()
    

class CustomMessageBox(QDialog):
    def __init__(self, parent=None):
        super(CustomMessageBox, self).__init__(parent)
        
        layout = QVBoxLayout()
        
        # 添加图片
        pixmap = QPixmap(self.resource_path('logo.png'))
        pixmap = pixmap.scaled(300, 200)
        label = QLabel()
        label.setPixmap(pixmap)

        # 创建一个 QWidget 作为图片布局的容器
        container = QWidget()
        container_layout = QVBoxLayout()

        # 设置图片居中对齐
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container_layout.addWidget(label)
        container.setLayout(container_layout)
        layout.addWidget(container)
        
        # 添加正文
        font = QFont("Microsoft YaHei", 10)
        self.message_label = QLabel(MainWindow.pop_text[0], self)
        self.message_label.setFont(font)
        self.message_label.setWordWrap(True)

        # 创建一个水平布局，用于包裹消息文本，并设置边距
        message_layout = QHBoxLayout()
        message_layout.addWidget(self.message_label)
        message_layout.setContentsMargins(17, 0, 17, 0)  # 设置左右边距为 17 像素
        layout.addLayout(message_layout)
        
        self.setWindowIcon(QIcon(self.resource_path('icon.ico')))

        self.setLayout(layout)

        self.setFixedSize(370, 665)


    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS # type: ignore
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):

    myappid = "ImageEdgesCropper"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    is_chinese = True

    window_title = ["图片透明/白色边缘批量裁剪工具", "Image Alpha/White Edges Batch Cropper"]
    input_button_text = ["选择输入文件夹", "Input Folder"]
    output_button_text = ["选择输出文件夹", "Output Folder"]
    input_path_text = ["仅处理文件夹直接包含的图片，后缀支持 .png .jpg .jpeg", "Only Handle Images Directly In Input Folder, With Extensions .png .jpg .jpeg"]
    output_path_text = ["若为空，则自动在输入文件夹下创建 output 文件夹以储存", "If Empty, Automatically Create An 'output' Folder In Input Folder For Storage"]
    group_box_text = ["裁剪模式", "Cropping Mode"]
    alpha_button_text = ["透明边缘", "Transparent"]
    white_button_text = ["白色边缘", "White"]
    start_button_text = ["启动", "Start"]
    pause_button_text = ["暂停", "Pause"]
    continue_button_text = ["继续", "Continue"]
    cease_button_text = ["中止", "Cease"]
    info_box_text = ["处理信息：", "Process Information:"]
    select_input_folder_text = ["选择输入文件夹", "Select Input Folder"]
    select_output_folder_text = ["选择输出文件夹", "Select Output Folder"]
    info_box_repo = ["- 请选择一个输入文件夹", "- Please Select An Input Folder"]
    click_lang_label = ["<b><font color=#454545>中</font><font color=#bbbbbb>/En</font></b>", "<b><font color=#bbbbbb>中/</font><font color=#454545>En</font></b>"]
    click_info_label = ["<b><font color=#454545>如何使用本工具？</font></b>", "<b><font color=#454545>How To Use ？</font></b>"]
    pop_window_title = ["使用说明", "Usage"]
    pop_title = ["<b><font color=#454545>如何使用本工具？</font></b>", "<b><font color=#454545>How to Use This Tool？</font></b>"]
    pop_text = [
        """
        <h2 style="text-align: center;line-height: 1.2;">如何使用本工具？</h2>
        <p>1. 选择<b>直接</b>包含被处理图片的文件夹。</p>
        <p>2. 选择输出文件夹。</p>
        <p>3. 选择裁剪模式，点击启动。</p>
        <p>所选文件夹下的<b>子文件夹中的图片将不被处理。</b></p>
        <p>该工具可<b>批量</b>裁剪边缘为<b>成行或成列出现的透明或纯白像素</b>的图片，将透明或白边裁去留下中间部分。</p>
        <p>为保留透明度信息，固定保存格式为 <b>.png</b>。</p>
        <p>如有 bug，欢迎反馈。</p>
        <br>
        <p style="text-align: right;line-height: 0.6;">作者：wunuo</p>
        <p style="text-align: right;line-height: 0.6;">邮箱：xuwunuo@foxmail.com</p>
        <p style="text-align: right;">2024.4.18</p>
        <br>
        """,
        """
        <h2 style="text-align: center;line-height: 1.2;">How to Use This Tool ?</h2>
        <p>1. Select the folder <b>directly</b> containing the images to be processed.</p>
        <p>2. Choose the output folder.</p>
        <p>3. Select the cropping mode and click start.</p>
        <p>Images in <b>subfolders</b> of the selected folder will not be processed.</p>
        <p>This tool can crop <b>batch</b> images with edges containing <b>rows or columns of transparent or pure white pixels,</b> leaving the middle part intact.</p>
        <p>To preserve transparency information, the fixed saving format is <b>.png</b>.</p>
        <p>If there are any bugs, please feel free to report them.</p>
        <br>
        <p style="text-align: right;line-height: 0.6;">Author: wunuo</p>
        <p style="text-align: right;line-height: 0.6;">Email: xuwunuo@foxmail.com</p>
        <p style="text-align: right;">2024.4.18</p>
        <br>
        """
    ]
    

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.window_title[0])
        # 初始化UI
        self.init_UI()


    def init_UI(self):

        # 创建输入按钮
        self.input_folder = ''
        self.select_input_button = QPushButton(self.input_button_text[0], self)
        self.select_input_button.setGeometry(40, 25, 120, 40)
        self.select_input_button.clicked.connect(self.select_input_folder)

        # 创建滚动区域和标签
        self.input_scroll_area = QScrollArea(self)
        self.input_scroll_area.setGeometry(170, 25, 490, 40)
        self.input_scroll_area.setWidgetResizable(True)
        self.input_scroll_widget = QWidget()
        self.input_scroll_area.setWidget(self.input_scroll_widget)
        self.input_scroll_layout = QVBoxLayout(self.input_scroll_widget)
        self.input_path_label = QLabel(self.input_path_text[0], self.input_scroll_widget)
        self.input_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.input_scroll_layout.addWidget(self.input_path_label)

        # 创建输出按钮
        self.output_folder = ''
        self.select_output_button = QPushButton(self.output_button_text[0], self)
        self.select_output_button.setGeometry(40, 75, 120, 40)
        self.select_output_button.clicked.connect(self.select_output_folder)

        # 创建输出滚动区域和标签
        self.output_scroll_area = QScrollArea(self)
        self.output_scroll_area.setGeometry(170, 75, 490, 40)
        self.output_scroll_area.setWidgetResizable(True)
        self.output_scroll_widget = QWidget()
        self.output_scroll_area.setWidget(self.output_scroll_widget)
        self.output_scroll_layout = QVBoxLayout(self.output_scroll_widget)
        self.output_path_label = QLabel(self.output_path_text[0], self.output_scroll_widget)
        self.output_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.output_scroll_layout.addWidget(self.output_path_label)

        # 创建模式选择
        self.group_box_mode = QGroupBox(self.group_box_text[0], self)
        self.group_box_mode.setGeometry(40, 130, 190, 50)
        self.group_box_mode.setStyleSheet("QGroupBox { border: 1px solid grey; }")

        # 创建模式选择单选框
        self.is_alpha = True
        self.alpha_button = QRadioButton(self.alpha_button_text[0], self.group_box_mode)
        self.alpha_button.setGeometry(20, 15, 100, 30)
        self.alpha_button.setChecked(True)
        self.alpha_button.clicked.connect(self.set_mode)
        self.white_button = QRadioButton(self.white_button_text[0], self.group_box_mode)
        self.white_button.setGeometry(100, 15, 100, 30)
        self.white_button.clicked.connect(self.set_mode)

        # 创建开始暂停继续按钮
        self.is_running = False
        self.is_paused = False
        self.is_started = False
        self.start_pause_button = QPushButton(self.start_button_text[0], self)
        self.start_pause_button.setGeometry(40, 190, 90, 30)
        self.start_pause_button.clicked.connect(self.on_start_pause_button_clicked)

        # 创建结束按钮
        self.cease_button = QPushButton(self.cease_button_text[0], self)
        self.cease_button.setGeometry(140, 190, 90, 30)
        self.is_paused = False
        self.cease_button.clicked.connect(self.on_cease_button_clicked)

        # 创建处理进度条
        self.progress_value = 0
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(40, 230, 620, 15)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 创建处理信息显示框
        self.info_box = QTextEdit(self.info_box_text[0], self)
        self.info_box.setReadOnly(True)
        self.info_box.setGeometry(240, 130, 420, 90)

        # 创建语言模式更改
        self.lang_label = ClickableLabel(self.click_lang_label[0], self)
        self.lang_label.setGeometry(510,250,35,30)
        self.lang_label.setOpenExternalLinks(True)
        self.lang_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lang_label.clicked.connect(self.set_ui_lang)
        
        # 创建信息弹窗可点击文字
        self.info_label = ClickableLabel(self.click_info_label[0], self)
        self.info_label.setGeometry(560,250,100,30)
        self.info_label.setOpenExternalLinks(True)
        self.info_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.info_label.clicked.connect(self.show_popup)

        # 初始化窗口尺寸
        self.setFixedSize(700, 290)
        self.set_center()

        # 设置窗口图标
        self.setWindowIcon(QIcon(self.resource_path('icon.ico')))


    def select_input_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, self.select_input_folder_text[0]if self.is_chinese else self.select_input_folder_text[1])
        if folder_path:
            self.input_folder = folder_path
            self.input_path_label.setText(f'{folder_path}')


    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, self.select_output_folder_text[0]if self.is_chinese else self.select_output_folder_text[1])
        if folder_path:
            self.output_folder = folder_path
            self.output_path_label.setText(f'{folder_path}')


    def set_center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))


    def set_mode(self):
        self.is_alpha = not self.is_alpha


    def on_start_pause_button_clicked(self):

        # 提示处理程序被点击启动过
        self.is_started = True

        if not self.is_running:
            if self.input_folder == '':
                self.info_box.append(self.info_box_repo[0] if self.is_chinese else self.info_box_repo[1])
            else:
                self.is_running = True
                self.start_pause_button.setText(self.pause_button_text[0] if self.is_chinese else self.pause_button_text[1])
                self.info_box.append("<b>- " + self.start_button_text[0] + "</b>" if self.is_chinese else "<b>- " + self.start_button_text[1] + "</b>")
                self.progress_value = 0
                self.progress_bar.setValue(0)
                self.select_input_button.setEnabled(False)
                self.select_output_button.setEnabled(False)
                self.alpha_button.setEnabled(False)
                self.white_button.setEnabled(False)
                self.input_file_paths = img_cropper.file_read(self.input_folder)

                # 启动处理线程
                self.processor_thread = ProcessorThread(self.input_file_paths, self.input_folder, self.output_folder, self.is_alpha, self.is_chinese)
                self.processor_thread.progress_updated.connect(self.update_progress)
                self.processor_thread.update_info.connect(self.update_info)
                self.processor_thread.finished.connect(self.fin_ui_reset)
                self.processor_thread.start()

        else:
            if not self.is_paused:
                self.is_paused = True
                self.start_pause_button.setText(self.continue_button_text[0] if self.is_chinese else self.continue_button_text[1])
                self.info_box.append("<b>- " + self.pause_button_text[0] + "</b>" if self.is_chinese else "<b>- " + self.pause_button_text[1] + "</b>")
                self.processor_thread.pause()
            else:
                self.is_paused = False
                self.start_pause_button.setText(self.pause_button_text[0] if self.is_chinese else self.pause_button_text[1])
                self.info_box.append("<b>- " + self.continue_button_text[0] + "</b>" if self.is_chinese else "<b>- " + self.continue_button_text[1] + "</b>")
                self.processor_thread.resume()


    def on_cease_button_clicked(self):
        if hasattr(self, 'processor_thread'):
            if self.is_running:
                self.info_box.append("<b>- " + self.cease_button_text[0] + "</b>" if self.is_chinese else "<b>- " + self.cease_button_text[1] + "</b>")
            self.processor_thread.cease()
            self.cease_ui_reset()
        else:
            self.cease_ui_reset()


    def show_popup(self):

        self.popup = CustomMessageBox()
        self.popup.setWindowTitle(self.pop_window_title[0] if self.is_chinese else self.pop_window_title[1])
        self.popup.message_label.setText(self.pop_text[0] if self.is_chinese else self.pop_text[1])
        self.popup.setFixedSize(370, 665 if self.is_chinese else 765)
        # popup.setStyleSheet("QLabel{"
        #             "min-width: 370px;"
        #             "min-height: 240px; "
        #             "}")
        self.popup.exec_()


    def set_ui_lang(self):

        self.is_chinese = not self.is_chinese

        if hasattr(self, 'processor_thread'):
            self.processor_thread.change_lang()

        if self.is_chinese:
            self.setWindowTitle(self.window_title[0])
            self.select_input_button.setText(self.input_button_text[0])
            self.select_output_button.setText(self.output_button_text[0])
            if self.input_folder == '':
                self.input_path_label.setText(self.input_path_text[0])
            if self.output_folder == '':
                self.output_path_label.setText(self.output_path_text[0])
            self.group_box_mode.setTitle(self.group_box_text[0])
            self.alpha_button.setText(self.alpha_button_text[0])
            self.white_button.setText(self.white_button_text[0])
            if not self.is_running:
                self.start_pause_button.setText(self.start_button_text[0])
            else:
                if not self.is_paused:
                    self.start_pause_button.setText(self.pause_button_text[0])
                else:
                    self.start_pause_button.setText(self.continue_button_text[0])
            self.cease_button.setText(self.cease_button_text[0])
            if not self.is_running and not self.is_started:
                self.info_box.setText(self.info_box_text[0])
            self.info_label.setText(self.click_info_label[0])
            self.lang_label.setText(self.click_lang_label[0])
            self.white_button.setGeometry(100, 15, 100, 30)

        else:
            self.setWindowTitle(self.window_title[1])
            self.select_input_button.setText(self.input_button_text[1])
            self.select_output_button.setText(self.output_button_text[1])
            if self.input_folder == '':
                self.input_path_label.setText(self.input_path_text[1])
            if self.output_folder == '':
                self.output_path_label.setText(self.output_path_text[1])
            self.group_box_mode.setTitle(self.group_box_text[1])
            self.alpha_button.setText(self.alpha_button_text[1])
            self.white_button.setText(self.white_button_text[1])
            if not self.is_running:
                self.start_pause_button.setText(self.start_button_text[1])
            else:
                if not self.is_paused:
                    self.start_pause_button.setText(self.pause_button_text[1])
                else:
                    self.start_pause_button.setText(self.continue_button_text[1])
            self.cease_button.setText(self.cease_button_text[1])
            if not self.is_running and not self.is_started:
                self.info_box.setText(self.info_box_text[1])
            self.info_label.setText(self.click_info_label[1])
            self.lang_label.setText(self.click_lang_label[1])
            self.white_button.setGeometry(120, 15, 100, 30)
        


    def update_progress(self, value):
        if self.is_running:
            self.progress_bar.setValue(value)


    def update_info(self, info):
        self.info_box.append(info)


    def cease_ui_reset(self):
        self.is_running = False
        self.is_paused = False
        self.progress_bar.reset()
        self.start_pause_button.setText(self.start_button_text[0] if self.is_chinese else self.start_button_text[1])
        self.select_input_button.setEnabled(True)
        self.select_output_button.setEnabled(True)
        self.alpha_button.setEnabled(True)
        self.white_button.setEnabled(True)


    def fin_ui_reset(self):
        self.is_running = False
        self.is_paused = False
        self.start_pause_button.setText(self.start_button_text[0] if self.is_chinese else self.start_button_text[1])
        self.select_input_button.setEnabled(True)
        self.select_output_button.setEnabled(True)
        self.alpha_button.setEnabled(True)
        self.white_button.setEnabled(True)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS # type: ignore
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)