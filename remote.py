import base64, threading, sys
import cv2, zmq, pyautogui
import numpy as np
import remote_gui


class RemoteDesktop:
    def __init__(self, resolution, is_controlled=False):
        self.res = resolution
        self.isctrld = is_controlled
        self.context = zmq.Context()
    
    def initiate_writing_connection(self, port):
        socket = self.context.socket(zmq.PUB)
        socket.bind(f'tcp://0.0.0.0:{port}')

        return socket
    
    def initiate_reading_connection(self, port):
        socket = self.context.socket(zmq.SUB)
        socket.connect(f'tcp://10.79.48.63:{port}')
        socket.setsockopt_string(zmq.SUBSCRIBE, '')

        return socket
    

    def send_stream(self, socket, stream):
        while True:
            try:
                data = stream()
                as_text = base64.b64encode(data)
                socket.send(as_text)
            except Exception as e:
                print(e)
                cv2.destroyAllWindows()
                break
    
    def get_data(self, socket):
        while True:
            data = socket.recv_string()
            data = base64.b64decode(data)
            yield data

    def apply_controls(self, socket):
        while True:
            data = socket.recv_string()
            data = base64.b64decode(data).decode()
            print(data)

    
    def initiate_connection(self, self_port, other_port):
        writer = self.initiate_writing_connection(self_port)
        reader = self.initiate_reading_connection(other_port)

        def stream_func():
            frame = np.array(pyautogui.screenshot())
            frame = cv2.resize(frame, self.res)
            encoded, buffer = cv2.imencode('.jpg', frame)

            return buffer

        if self.isctrld:
            streamer = threading.Thread(target=self.send_stream, args=(writer, stream_func))
            streamer.start()

            controller = threading.Thread(target=self.apply_controls, args=(reader, ))
            controller.start()
        else:
            data = self.get_data(reader)
            gui = remote_gui.GUI(self.res, self.isctrld, writer)
            gui.stream_loop(data)

        # if self.isctrld:
        #     def stream_func():
        #         frame = np.array(pyautogui.screenshot())
        #         frame = cv2.reisze(frame, self.res)
        #         encoded, buffer = cv2.imencode('.jpg', frame)

        #         return buffer
        # else:
        #     def stream_func():
        #         mouse_pos = pyautogui.position()


if __name__ == "__main__":
    rem = RemoteDesktop((640, 480))
    rem.initiate_connection(int(sys.argv[1]), int(sys.argv[2]))