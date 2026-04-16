import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_env(env_file: str = None):
    """加载 .env 文件到环境变量"""
    if env_file is None:
        base_dir = Path(__file__).resolve().parent.parent
        env_file = base_dir / ".env"
    
    env_path = Path(env_file)
    
    if not env_path.exists():
        logger.warning(f"Environment file not found: {env_file}")
        return False
    
    with open(env_path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith("#"):
                continue
            
            # 解析 key=value
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                # 设置环境变量
                os.environ.setdefault(key, value)
                logger.debug(f"Loaded env variable: {key}")
    
    logger.info(f"Environment variables loaded from {env_file}")
    return True


def get_env(key: str, default: str = None) -> str:
    """获取环境变量"""
    return os.environ.get(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """获取布尔类型环境变量"""
    value = os.environ.get(key, str(default))
    return value.lower() in ("true", "1", "yes", "on")


def get_env_int(key: str, default: int = 0) -> int:
    """获取整数类型环境变量"""
    try:
        return int(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


def get_env_list(key: str, default: list = None) -> list:
    """获取列表类型环境变量"""
    if default is None:
        default = []
    
    value = os.environ.get(key, "")
    if not value:
        return default
    
    # 解析 JSON 格式列表或逗号分隔
    if value.startswith("[") and value.endswith("]"):
        try:
            import json
            return json.loads(value)
        except json.JSONDecodeError:
            return default
    
    return [item.strip() for item in value.split(",") if item.strip()]
