import hydra
import logging
import torch
from hydra.utils import instantiate
from pbtrack.datastruct.tracker_state import TrackerState

log = logging.getLogger(__name__)

@hydra.main(version_base=None, config_path="configs", config_name="config")
def track(cfg, train_reid=True, train_pose=False):
    device = "cuda" if torch.cuda.is_available() else "cpu"  # TODO support Mac chips

    # Init
    tracking_dataset = instantiate(cfg.dataset)
    model_pose = instantiate(cfg.detection, device=device)
    model_reid = instantiate(cfg.reid, tracking_dataset=tracking_dataset, device=device, model_pose=model_pose)
    model_track = instantiate(cfg.track, device=device)
    # evaluator = instantiate(cfg.eval)
    # vis_engine = instantiate(cfg.visualization)

    # Train Reid
    if train_reid:
        model_reid.train()

    # Train Pose
    if train_pose:
        model_pose.train()

    # Tracking
    # TODO can we slice tracker_state?
    tracking_state = TrackerState(tracking_dataset.val_set)
    model_pose.run(tracking_state)  # list Image or slice Images OR batch numpy images -> list Detection or slice Detections
    model_reid.run(tracking_state)  # list Detection or slice Detections OR batch numpy images + skeletons + masks -> list Detection or slice Detections
    model_track.run(tracking_state)  # online: list frame Detection -> list frame Detection | offline: video detections -> video detections

    # Performance
    # evaluator.run(tracker)

    # Visualization
    # vis_engine.run(tracker)


if __name__ == "__main__":
    track()
