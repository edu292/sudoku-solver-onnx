import numpy as np
import cv2
from scipy import ndimage
import onnxruntime as ort
from tkinter.filedialog import askopenfilename


IMG_WIDTH = 450
IMG_HEIGHT = 450
model_path = 'mnist-12.onnx'


class SudokuBoardReader:
    def __init__(self):
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.board = None
        self.loaded = False

    def reset(self):
        self.board = [0 for _ in range(81)]

    def load_image_file(self):
        file_path = askopenfilename(title="Select a sudoku board image",
                                    filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp")])
        if not file_path:
            return

        img = cv2.imread(file_path)
        self.get_board(img)

    def get_board(self, img):
        self.reset()
        self.loaded = False
        img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))

        processed_image = pre_process_image(img)
        board_image = extract_board(img, processed_image)

        cells = split_cells(board_image)
        self.recognize_digits(cells)
        self.loaded = True

    def recognize_digits(self, cells):
        for idx, cell in enumerate(cells):
            digit_tensor = preprocess_cell(cell)
            if digit_tensor is None:
                continue
            predictions = self.session.run([self.output_name], {self.input_name: digit_tensor})
            predicted_digit = int(np.argmax(predictions[0]))
            self.board[idx] = predicted_digit


def pre_process_image(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)
    img_threshold = cv2.adaptiveThreshold(img_blur, 255,
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY_INV, 11, 2)
    return img_threshold


def extract_board(img, img_threshold):
    contours, _ = cv2.findContours(img_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    biggest_rect = None
    max_area = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area > max_area:
            biggest_rect = (x, y, w, h)
            max_area = area

    x, y, w, h = biggest_rect
    cropped_board = img[y:y + h, x:x + w]

    resized_board = cv2.resize(cropped_board, (IMG_WIDTH, IMG_HEIGHT))
    resized_board = cv2.cvtColor(resized_board, cv2.COLOR_BGR2GRAY)
    return resized_board


def split_cells(grid):
    rows = np.vsplit(grid, 9)
    cells = [cell for row in rows for cell in np.hsplit(row, 9)]
    return cells


def preprocess_cell(cell):
    cell = crop_cell_margins(cell)
    binary = binarize_image(cell)

    digit = extract_digit(binary)
    if digit is None:
        return None

    digit_resized = resize_and_center(digit)
    centered = center_by_mass(digit_resized)
    norm = centered.astype(np.float32) / 255.0

    return norm.reshape(1, 1, 28, 28)


def is_inside_margin(x, y, w, h, img_shape, margin=1):
    H, W = img_shape
    return x <= margin or y <= margin or x + w >= W - margin or y + h >= H - margin


def extract_digit(thresh):
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    h_img, w_img = thresh.shape
    valid_contours = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        if is_inside_margin(x, y, w, h, (h_img, w_img)):
            continue
        valid_contours.append((cnt, area))

    if not valid_contours:
        return None

    best_cnt = max(valid_contours, key=lambda x: x[1])[0]
    x, y, w, h = cv2.boundingRect(best_cnt)
    if h < 15:
        return None

    digit = thresh[y:y + h, x:x + w]
    digit = cv2.copyMakeBorder(digit, 4, 4, 4, 4, cv2.BORDER_CONSTANT, value=0)
    return digit


def binarize_image(cell):
    if np.mean(cell) > 127:
        cell = cv2.bitwise_not(cell)
    cell = cv2.GaussianBlur(cell, (3, 3), 0)
    _, thresh = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh


def crop_cell_margins(cell, margin=4):
    return cell[margin:-margin, margin:-margin]


def resize_and_center(digit, size=20):
    h, w = digit.shape
    scale = size / max(h, w)
    img_resized = cv2.resize(digit, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    h, w = img_resized.shape

    digit_resized = np.zeros((size, size), dtype=np.uint8)
    x_offset = (size - w) // 2
    y_offset = (size - h) // 2
    digit_resized[y_offset:y_offset + h, x_offset:x_offset + w] = img_resized
    return digit_resized


def center_by_mass(digit):
    canvas = np.zeros((28, 28), dtype=np.uint8)
    canvas[4:24, 4:24] = digit

    cy, cx = ndimage.center_of_mass(canvas)
    if np.isnan(cx) or np.isnan(cy):
        return None

    rows, cols = canvas.shape
    shift_x = int(np.round(cols / 2.0 - cx))
    shift_y = int(np.round(rows / 2.0 - cy))

    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    centered = cv2.warpAffine(canvas, M, (cols, rows), borderValue=0)
    return centered
