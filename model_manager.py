from PIL import Image
import torch
import torchvision.transforms as transforms
from scipy import misc

from simple_model import SimpleStyleTransferModel


# В данном классе мы хотим полностью производить всю обработку картинок, которые поступают к нам из телеграма.
# Это всего лишь заготовка, поэтому не стесняйтесь менять имена функций, добавлять аргументы, свои классы и
# все такое.
class StyleTransferManager:
    def __init__(self):
        # Сюда необходимо перенести всю иницализацию, вроде загрузки свеерточной сети и т.д.
        self.image_size = 255
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(self.device)
        pass

    def simple_transfer_style(self, content_img_stream, style_img_stream):
        # Этот метод по переданным картинкам в каком-то формате (PIL картинка, BytesIO с картинкой
        # или numpy array на ваш выбор). В телеграм боте мы получаем поток байтов BytesIO,
        # а мы хотим спрятать в этот метод всю работу с картинками, поэтому лучше принимать тут эти самые потоки
        # и потом уже приводить их к PIL, а потом и к тензору, который уже можно отдать модели.
        # В первой итерации, когда вы переносите уже готовую модель из тетрадки с занятия сюда нужно просто
        # перенести функцию run_style_transfer (не забудьте вынести инициализацию, которая
        # проводится один раз в конструктор.
        content_img = self.load_image(content_img_stream)
        style_img = self.load_image(style_img_stream)
        model = SimpleStyleTransferModel()
        output_img = model.process_image(content_img, style_img, 500)

        output_img = misc.toimage(output_img[0])
        return output_img

    def test_simple_transfer_style(self,  content_img_path, style_img_path, output_image_path):
        # Этот метод для тестирования процедуры переноса стиля из файлов
        content_img = self.load_image(content_img_path)
        style_img = self.load_image(style_img_path)
        model = SimpleStyleTransferModel()
        output_img = model.process_image(content_img, style_img, 500)

        output_img = misc.toimage(output_img[0])
        output_img.save(output_image_path)

    def load_image(self, img_stream):
        image = Image.open(img_stream)
        loader = transforms.Compose([
            transforms.Resize(self.image_size),  # нормируем размер изображения
            transforms.CenterCrop(self.image_size),
            transforms.ToTensor()])  # превращаем в удобный формат
        image = loader(image).unsqueeze(0)
        return image.to(self.device, torch.float)

    def load_image_1(self, img_stream):
        imsize = self.image_size
        image = Image.open(img_stream)
        isize = image.size
        sizeX = imsize
        sizeY = int(imsize * isize[1] / isize[0])
        loader = transforms.Compose([
            transforms.Resize((sizeY, sizeX)),  # нормируем размер изображения
            # transforms.CenterCrop(imsize),
            transforms.ToTensor()])  # превращаем в удобный формат
        image = loader(image).unsqueeze(0)
        return image.to(self.device, torch.float)

#if __name__ == '__main__':
#    model = StyleTransferManager()
#    content_image_path = 'Z:\\_DEVELOP\\_PYTHON\\dlsw3_bot_style\\images\\content-images\\loshad.jpg'
#    style_image_path = 'Z:\\_DEVELOP\\_PYTHON\\dlsw3_bot_style\\images\\style-images\\candy.jpg'
#    output_image_path = 'Z:\\_DEVELOP\\_PYTHON\\dlsw3_bot_style\\images\\output-images\\loshad.jpg'
#    output = model.test_simple_transfer_style(content_image_path, style_image_path, output_image_path)
