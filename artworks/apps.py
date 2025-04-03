import os
import faiss
import numpy as np
import clip
import torch
from django.apps import AppConfig
from django.conf import settings

class ArtworksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artworks"

    def ready(self):
        # 1. device를 속성으로 저장
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        BASE_DIR = settings.BASE_DIR  # 프로젝트 루트
        index_path = os.path.join(BASE_DIR, "indexes", "artwork.index")
        ids_path = os.path.join(BASE_DIR, "indexes", "artwork_ids.npy")

        # 2. Faiss 인덱스와 ID 매핑 파일 로드
        if os.path.exists(index_path) and os.path.exists(ids_path):
            self.faiss_index = faiss.read_index(index_path)
            self.artwork_ids = np.load(ids_path)
        else:
            self.faiss_index = None
            self.artwork_ids = None

        # 3. CLIP 모델 로컬 파일 로드
        model_dir = os.path.join(BASE_DIR, "clip_models")
        self.clip_model, self.clip_preprocess = clip.load(
            "ViT-B/32",
            device=self.device,          # 여기서 self.device 사용
            download_root=model_dir,
        )
        print("✅ CLIP 모델 로컬 파일로 로드 완료!")