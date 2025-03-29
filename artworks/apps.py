import os
import clip
import torch
from django.apps import AppConfig
from django.conf import settings

class ArtworksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artworks"

    def ready(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        BASE_DIR = settings.BASE_DIR

        # CLIP 모델 경로 설정
        model_dir = os.path.join(BASE_DIR, "clip_models")
        model_path = os.path.join(model_dir, "ViT-B-32.pt")

        # 모델 경로가 존재하면 강제로 로컬에서 로드
        try:
            if os.path.exists(model_path):
                print("✅ 로컬 CLIP 모델을 로드합니다.")
                self.clip_model, self.clip_preprocess = clip.load(
                    model_path,
                    device=self.device,
                    jit=False  # M1 환경 안정성을 위해 JIT 비활성화
                )
            else:
                print("🔄 CLIP 모델을 다운로드 중입니다...")
                self.clip_model, self.clip_preprocess = clip.load(
                    "ViT-B/32",
                    device=self.device,
                    download_root=model_dir,
                    jit=False
                )
            print("✅ CLIP 모델 로드 완료!")
        except Exception as e:
            print(f"⚠️ CLIP 모델 로드 중 오류 발생: {e}")