import os
import webbrowser
import random
from flet import (
    AppBar, Column, ElevatedButton, FilePicker, FilePickerResultEvent, Page, Row,
    Slider, Text, TextField, Image, ProgressBar, alignment, Container, IconButton, icons, Card, GestureDetector, ListView, Stack, ButtonStyle
)

class PhotoRatingApp:
    def __init__(self, page: Page):
        self.page = page
        self.page.title = "Оценка фотографий"
        self.criteria = []  # Список критериев для оценки
        self.folder_path = None  # Папка с изображениями
        self.image_files = []  # Список изображений
        self.current_image_index = 0  # Текущий индекс изображения
        self.ratings = {}  # Оценки для каждого изображения

        self.start_page()

    def start_page(self):
        self.page.controls.clear()
        self.criteria = []
        self.folder_path = None
        self.image_files = []

        # Ввод критериев
        self.criteria_input = TextField(label="Введите критерий", on_submit=self.add_criterion)
        self.criteria_list = Column()

        # Индикация выбранной папки
        self.folder_path_text = Text("Папка не выбрана", size=16, color="red")

        # Выбор папки
        self.folder_picker = FilePicker(on_result=self.select_folder)
        self.page.overlay.append(self.folder_picker)
        self.folder_button = ElevatedButton("Выбрать папку", on_click=lambda _: self.folder_picker.get_directory_path())

        # Кнопка старта
        self.start_button = ElevatedButton("Начать оценку", disabled=True, on_click=self.start_evaluation)

        self.page.add(
            AppBar(title=Text("Настройка оценки")),
            Column(
                [
                    Text("Шаг 1: Добавьте критерии оценки", size=20),
                    Row([self.criteria_input, ElevatedButton("Добавить", on_click=self.add_criterion)], alignment="center"),
                    self.criteria_list,
                    Text("Шаг 2: Выберите папку с изображениями", size=20),
                    self.folder_button,
                    self.folder_path_text,
                    Text("Шаг 3: Начать оценку", size=20),
                    self.start_button
                ],
                alignment="center",
                horizontal_alignment="center",
                expand=True
            )
        )
        self.page.update()

    def add_criterion(self, event=None):
        criterion = self.criteria_input.value.strip()
        if criterion:
            self.criteria.append(criterion)
            criterion_card = Card(
                content=Container(
                    content=Row(
                        [
                            Text(criterion, size=16, expand=True),
                            IconButton(
                                icon=icons.DELETE,
                                tooltip="Удалить критерий",
                                on_click=lambda _, c=criterion: self.remove_criterion(c)
                            ),
                        ],
                        alignment="spaceBetween",
                    ),
                    padding=10,
                ),
                elevation=2,
                margin=5,
                width=300,
            )
            self.criteria_list.controls.append(criterion_card)
            self.page.update()
            self.criteria_input.value = ""

    def remove_criterion(self, criterion):
        self.criteria.remove(criterion)
        self.criteria_list.controls = [
            control for control in self.criteria_list.controls
            if not isinstance(control, Card) or control.content.content.controls[0].value != criterion
        ]
        self.page.update()

    def select_folder(self, e: FilePickerResultEvent):
        if e.path:
            self.folder_path = e.path
            self.image_files = [os.path.join(self.folder_path, f) for f in os.listdir(self.folder_path)
                                if f.lower().endswith(('png', 'jpg', 'jpeg'))]
            self.folder_path_text.value = f"Выбрана папка: {self.folder_path}"
            self.folder_path_text.color = "green"
            self.start_button.disabled = not bool(self.image_files)
            self.page.update()

    def start_evaluation(self, event):
        self.page.controls.clear()
        self.current_image_index = 0
        self.ratings = {image: {criterion: 5 for criterion in self.criteria} for image in self.image_files}
        self.evaluation_page()

    def evaluation_page(self):
        self.image_display = Image(src=self.image_files[self.current_image_index], width=500, height=500)

        # Ползунки для оценки
        self.criteria_sliders = []
        sliders_column = Column()
        for criterion in self.criteria:
            title = Text(criterion, size=18)
            slider = Slider(label=criterion, min=1, max=10, divisions=9, value=5, on_change=self.update_rating)
            self.criteria_sliders.append(slider)
            sliders_column.controls.append(Column([title, slider]))

        # Навигационные кнопки
        self.random_button = ElevatedButton("Рандомная оценка", on_click=self.randomize_ratings)
        self.prev_button = ElevatedButton("Назад", on_click=self.previous_image, disabled=self.current_image_index == 0)
        self.next_button = ElevatedButton("Далее", on_click=self.next_image)
        self.finish_button = ElevatedButton("Завершить", on_click=self.show_results)

        self.progress = ProgressBar(value=self.current_image_index / len(self.image_files), bar_height=20)

        self.page.add(
            Column(
                [
                    self.image_display,
                    sliders_column,
                    Row([self.random_button, self.prev_button, self.next_button, self.finish_button], alignment="center"),
                    self.progress
                ],
                alignment="center",
                horizontal_alignment="center",
                expand=True,
            )
        )
        self.page.update()

    def randomize_ratings(self, e):
        current_image = self.image_files[self.current_image_index]
        for slider, criterion in zip(self.criteria_sliders, self.criteria):
            random_value = random.randint(1, 10)
            slider.value = random_value
            self.ratings[current_image][criterion] = random_value
        self.page.update()

    def update_rating(self, e):
        slider = e.control
        criterion = slider.label
        value = slider.value
        current_image = self.image_files[self.current_image_index]
        self.ratings[current_image][criterion] = value

    def next_image(self, e):
        self.current_image_index += 1
        if self.current_image_index < len(self.image_files):
            self.refresh_evaluation_page()
        else:
            self.show_results()

    def previous_image(self, e):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.refresh_evaluation_page()

    def refresh_evaluation_page(self):
        self.image_display.src = self.image_files[self.current_image_index]
        for slider, criterion in zip(self.criteria_sliders, self.criteria):
            slider.value = self.ratings[self.image_files[self.current_image_index]][criterion]
        self.prev_button.disabled = self.current_image_index == 0
        self.progress.value = self.current_image_index / len(self.image_files)
        self.page.update()

    def open_in_explorer(self, image_path):
        # Открыть путь к файлу в проводнике
        webbrowser.open(f'file://{os.path.abspath(image_path)}')

    def show_results(self, e=None):
        # Подсчет результатов
        scores = {
            image: sum(self.ratings.get(image, {}).get(criterion, 0) 
                       for criterion in self.criteria)
            for image in self.image_files
        }
        sorted_images = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        winners = sorted_images[:3]

        # Очистка текущих элементов
        self.page.controls.clear()

        # Создаем Stack для абсолютного позиционирования
        def update_layout(e):
            # Пересоздаем Stack при каждом изменении размера
            page_stack.controls.clear()
            
            # Победитель - первый элемент в стеке
            winner_container = Container(
                content=Column(
                    [
                        Text("Победитель:", size=24, weight="bold"),
                        GestureDetector(
                            content=Image(
                                src=winners[0][0], 
                                width=min(300, self.page.width * 0.7),  # Адаптивная ширина
                                height=min(300, self.page.width * 0.7),  # Адаптивная высота
                                fit="contain"
                            ),
                            on_tap=lambda e: self.open_in_explorer(winners[0][0])
                        ),
                        Text(f"{os.path.basename(winners[0][0])} - {winners[0][1]} баллов", size=18, weight="bold"),
                    ],
                    alignment="center",
                    horizontal_alignment="center",
                    spacing=10
                ),
                top=0,
                left=0,
                width=self.page.width,
                padding=10,
            )

            # Список участников - второй элемент в стеке
            participants_container = Container(
                content=ListView(
                    controls=[
                        Card(
                            content=Container(
                                content=Row(
                                    [
                                        Image(
                                            src=image, 
                                            width=80, 
                                            height=80, 
                                            fit="cover", 
                                            border_radius=10
                                        ),
                                        Column(
                                            [
                                                Text(f"{idx}-е место", size=18, weight="bold", color="blue"),
                                                Text(f"{os.path.basename(image)}", size=16, weight="bold", color="gray"),
                                                Text(f"{score} баллов", size=14, color="green"),
                                            ],
                                            alignment="start",
                                            horizontal_alignment="start",
                                            spacing=5,
                                            width=self.page.width * 0.6  # Растягиваем на ширину
                                        ),
                                    ],
                                    alignment="start",
                                    spacing=10,
                                    width=self.page.width * 0.9  # Почти на всю ширину
                                ),
                                padding=10,
                                margin=10,
                                bgcolor="#2F3236",
                                border_radius=15,
                                width=self.page.width * 0.9  # Почти на всю ширину
                            ),
                            elevation=3,
                            margin=10,
                            width=self.page.width * 0.9  # Почти на всю ширину
                        ) for idx, (image, score) in enumerate(sorted_images[1:], start=2)
                    ],
                    spacing=10,
                    expand=True,
                ),
                top=400,
                left=self.page.width * 0.05,  # Центрируем
                width=self.page.width * 0.9,  # Почти на всю ширину
                height=self.page.height - 450,
            )

            # Кнопка возврата на начальный экран
            return_button = Container(
                content=ElevatedButton(
                    "Вернуться на начальную страницу", 
                    on_click=lambda _: self.start_page(),
                    width=self.page.width * 0.9,  # Почти на всю ширину
                    style=ButtonStyle(
                        bgcolor="#4A4E69",
                        color="white",
                    )
                ),
                top=self.page.height - 50,  # Позиционирование внизу
                left=self.page.width * 0.05,  # Центрируем
                width=self.page.width * 0.9,  # Почти на всю ширину
            )

            # Добавляем элементы в Stack
            page_stack.controls.extend([
                winner_container, 
                participants_container, 
                return_button
            ])
            
            # Обновляем страницу
            self.page.update()

        # Создаем Stack
        page_stack = Stack(
            controls=[],
            width=self.page.width,
            height=self.page.height,
            expand=True,
        )

        # Добавляем обработчик изменения размера
        self.page.on_resize = update_layout

        # Первоначальное обновление макета
        update_layout(None)

        # Добавляем Stack на страницу
        self.page.add(page_stack)
        self.page.update()

def main(page: Page):
    page.window_width = None  # Автоматическая ширина
    page.window_height = None  # Автоматическая высота
    page.window_resizable = True  # Окно остается изменяемым
    PhotoRatingApp(page)

if __name__ == "__main__":
    import flet
    flet.app(target=main)
