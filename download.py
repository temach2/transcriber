from huggingface_hub import snapshot_download
import os

# Укажите ID модели
model_id = "pyannote/speaker-diarization-3.1"
# model_id = "Qwen/Qwen3-ForcedAligner-0.6B"
# model_id = "Qwen/Qwen3-ASR-1.7B"
# Укажите путь к вашей папке проекта
local_dir = r"d:\botsdevelopment\med-transcriber\models\pyannote-speaker-diarization-3.1"

# Создаст папку, если её не существует
os.makedirs(local_dir, exist_ok=True)

print(f"Начинаю загрузку модели {model_id}...")
print(f"Файлы будут сохранены в: {local_dir}")

# Скачиваем модель. Параметр local_dir_use_symlinks=False гарантирует,
# что файлы будут скопированы, а не созданы как ссылки.
snapshot_download(
    repo_id=model_id,
    local_dir=local_dir,
    local_dir_use_symlinks=False
)
print("✅ Загрузка успешно завершена!")