import os
import re
import torch
from torchvision import transforms
import torch.onnx

import fast_neural_style.utils as utils
from fast_neural_style.transformer_net import TransformerNet


def stylize(content_img, style_name):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with torch.no_grad():
        style_model = TransformerNet()
        model_path = os.getcwd()
        model_name = style_name + ".pth"
        model_path = os.path.join(model_path, "fast_neural_style")
        model_path = os.path.join(model_path, "saved_models")
        model_path = os.path.join(model_path, model_name)
        state_dict = torch.load(model_path)
        # remove saved deprecated running_* keys in InstanceNorm from the checkpoint
        for k in list(state_dict.keys()):
            if re.search(r'in\d+\.running_(mean|var)$', k):
                del state_dict[k]
        style_model.load_state_dict(state_dict)
        style_model.to(device)
        output = style_model(content_img).cpu()

    #utils.save_image(args.output_image, output[0])
    return output

