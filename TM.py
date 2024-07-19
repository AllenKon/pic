import threading
import serial
import numpy as np
from ast import literal_eval
import PySimpleGUI as sg
import statistics

# 初始化共享数据
shared_data = np.zeros((3, 15))

# 定义GUI布局和窗口
gifs_sequences = {
    'S0': [('Normal.gif', 44), ('NormalN.gif', 9)],
    'S1': [('Normal-Bored.gif', 23), ('Boredom.gif', 46), ('BoredomN.gif', 1000)],
    'S2': [('Normal-Happiness.gif', 23), ('Happiness.gif', 46), ('HappinessN.gif', 200)],
    'S3': [('Normal-Anger.gif', 23), ('Anger.gif', 64), ('AngerN.gif', 200)],
}

layout = [[sg.Image(key='-GIF-')]]
window = sg.Window('Window with GIFs', layout, finalize=True)

current_sequence = []
sequence_index = 0
frame_count = 0
need_update_sequence = True

class SerialPort:
    def __init__(self, read_port, write_port, baudrate):
        self.read_ser = serial.Serial(read_port, baudrate, timeout=1)
        self.write_ser = serial.Serial(write_port, baudrate, timeout=1)
        self.read_thread = threading.Thread(target=self.read_from_port)
        self.alive = False
        self.data_list = []

    def start(self):
        self.alive = True
        self.read_thread.start()

    def stop(self):
        self.alive = False
        self.read_thread.join()

    # def read_from_port(self):
    #     global current_sequence, sequence_index, frame_count, need_update_sequence
    #     threshold1 = 10
    #     threshold2 = 40
    #     threshold3 = 60
    #     while self.alive:
    #         try:
    #             data = self.read_ser.readline().decode('utf-8').strip()
    #             data = literal_eval(data)
    #             if data:
    #                 self.data_list.append(statistics.mean(data))
    #                 if len(self.data_list) == 15:
    #                     average = sum(self.data_list) / len(self.data_list)
    #                     print(f"Average: {average}")
    #                     self.data_list.clear()
    #                     if average < threshold1 and current_sequence != gifs_sequences['S0']:
    #                         need_update_sequence = True
    #                         sequence_to_set = 'S0'
    #                         self.write_ser.write(b"0")
    #                     elif threshold1 <= average < threshold2 and current_sequence != gifs_sequences['S1']:
    #                         need_update_sequence = True
    #                         sequence_to_set = 'S1'
    #                         self.write_ser.write(b"1")
    #                     elif threshold2 <= average < threshold3 and current_sequence != gifs_sequences['S2']:
    #                         need_update_sequence = True
    #                         sequence_to_set = 'S2'
    #                         self.write_ser.write(b"2")
    #                     elif average >= threshold3 and current_sequence != gifs_sequences['S3']:
    #                         need_update_sequence = True
    #                         sequence_to_set = 'S3'
    #                         self.write_ser.write(b"3")
    #                     if need_update_sequence:
    #                         current_sequence = gifs_sequences[sequence_to_set]
    #                         sequence_index = 0
    #                         frame_count = 0
    #                         need_update_sequence = False
    #                         # Send data to the second serial port
    #         except ValueError as e:
    #             print(f"Error parsing data: {e}")

    def read_from_port(self):
    global current_sequence, sequence_index, frame_count, need_update_sequence
    threshold1 = 10
    threshold2 = 40
    threshold3 = 60
    while self.alive:
        try:
            # 读取数据并解码
            raw_data = self.read_ser.readline().decode('utf-8').strip()
            print(f"Raw data: {raw_data}")  # 调试信息
            
            # 清理和解析数据
            data = self.clean_data(raw_data)
            if data:
                self.data_list.append(statistics.mean(data))
                if len(self.data_list) == 15:
                    average = sum(self.data_list) / len(self.data_list)
                    print(f"Average: {average}")
                    self.data_list.clear()
                    if average < threshold1 and current_sequence != gifs_sequences['S0']:
                        need_update_sequence = True
                        sequence_to_set = 'S0'
                        self.write_ser.write(b"0")
                    elif threshold1 <= average < threshold2 and current_sequence != gifs_sequences['S1']:
                        need_update_sequence = True
                        sequence_to_set = 'S1'
                        self.write_ser.write(b"1")
                    elif threshold2 <= average < threshold3 and current_sequence != gifs_sequences['S2']:
                        need_update_sequence = True
                        sequence_to_set = 'S2'
                        self.write_ser.write(b"2")
                    elif average >= threshold3 and current_sequence != gifs_sequences['S3']:
                        need_update_sequence = True
                        sequence_to_set = 'S3'
                        self.write_ser.write(b"3")
                        # Send data to the second serial port
        except ValueError as e:
            print(f"Error parsing data: {e}")

def clean_data(self, raw_data):
    try:
        # 先进行数据清理，比如去除多余的空格或换行符
        cleaned_data = raw_data.strip()
        # 使用 literal_eval 解析数据
        return literal_eval(cleaned_data)
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing data: {e}")
        print(f"Raw data: {raw_data}")  # 打印原始数据以便调试
        return None


if __name__ == '__main__':
    serial_port = SerialPort('COM12', 'COM17', 115200)  # Adjust COM ports as needed
    try:
        serial_port.start()
        while True:
            event, values = window.read(timeout=10)
            if event in (sg.WIN_CLOSED, 'Exit'):
                break
            if current_sequence and sequence_index < len(current_sequence):
                gif, duration = current_sequence[sequence_index]
                if frame_count < duration:
                    if frame_count == 0:
                        window['-GIF-'].update(filename=gif)
                    window['-GIF-'].UpdateAnimation(gif, time_between_frames=40)
                    frame_count += 1
                else:
                    frame_count = 0
                    sequence_index += 1
                    if sequence_index >= len(current_sequence):
                        current_sequence = []
                        sequence_index = 0
                        need_update_sequence = True
                print(frame_count)
    except KeyboardInterrupt:
        print("Stopping program")
    finally:
        serial_port.stop()
        window.close()
