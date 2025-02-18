from flask import Flask, jsonify, request
from flasgger import Swagger
import torch
from inference import main
import argparse

app = Flask(__name__)
swagger = Swagger(app)  # Initialize Swagger

@app.route('/inference', methods=['POST'])
def inference():
    """
    Run inference
    ---
    responses:
      200:
        description: inference successfully executed
    """
    # text = request.args.get('text')

    args_dict = {
        "driven_audio": "./examples/driven_audio/sarah-ita.wav",
        "source_image": "./examples/source_image/Young-Nurse-big.png",
        "ref_eyeblink": None,
        "ref_pose": None,
        "checkpoint_dir": "./checkpoints",
        "result_dir": "./results",
        "pose_style": 0,
        "batch_size": 2,
        "size": 256,
        "expression_scale": 1.0,
        "input_yaw": None,
        "input_pitch": None,
        "input_roll": None,
        "enhancer": None,
        "background_enhancer": None,
        "cpu": False,
        "face3dvis": False,
        "still": False,
        "preprocess": "crop",
        "verbose": False,
        "old_version": False,
        "net_recon": "resnet50",
        "init_path": None,
        "use_last_fc": False,
        "bfm_folder": "./checkpoints/BFM_Fitting/",
        "bfm_model": "BFM_model_front.mat",
        "focal": 1015.0,
        "center": 112.0,
        "camera_d": 10.0,
        "z_near": 5.0,
        "z_far": 15.0,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }
    
    args = argparse.Namespace(**args_dict)
    
    res = main(args)

    return jsonify({"message": "OK-" + res}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)